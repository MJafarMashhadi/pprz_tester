import logging
from collections import defaultdict
from typing import Callable, Any

from lxml import etree

import pprzlink as pl
from ivy_subscribe import IvySubscribe

logger = logging.getLogger('pprz_tester')


class Aircraft(object):
    def __init__(self,
                 ivy_link: pl.ivy.IvyMessagesInterface,
                 ac_id: int,
                 auto_request_config: bool = True
                 ):
        self._ivy = ivy_link
        self.id = ac_id
        self.flight_plan_uri = None
        self._mode = None
        self._current_block = None
        self._circle_count = 0
        self.flight_plan_blocks = dict()
        self._observers = defaultdict(list)

        if auto_request_config:
            self.request_config()

        self._ac = AircraftCommands(self)
        # TODO: find a better way to use the decorator instead of patching like this. It defeats the purpose.
        IvySubscribe(ivy_link=self._ivy, message_types=[("telemetry", "PPRZ_MODE"), ("telemetry", "NAVIGATION")]) \
            (self.set_values_callback)

    def observe(self, property_name: str, callback: Callable[[str, Any, Any], None]):
        self._observers[property_name].append(callback)

    def look_away(self, property_name: str, callback: Callable[[str, Any, Any], None]):
        self._observers[property_name].remove(callback)

    def notify_all(self, name: str, *, old_value: Any, new_value: Any):
        for cb in self._observers[name]:
            try:
                cb(property_name=name, old_value=old_value, new_value=new_value)
            except Exception as e:
                logger.error(f'Exception while notifying an observer of {name}')
                import traceback
                traceback.print_exc()

    @property
    def commands(self):
        return self._ac

    def request_config(self):
        def aircraft_config_callback(ac_id, msg):
            assert int(ac_id) == self.id

            logger.info(f"Got new aircraft config {ac_id}: {msg}")
            flight_plan_uri = msg['flight_plan']

            logger.info(f"Loading flight plan {ac_id}: {flight_plan_uri}")
            fp_tree = etree.parse(flight_plan_uri)
            for block in fp_tree.xpath("//block"):
                self.flight_plan_blocks[block.attrib['name']] = int(block.attrib['no'])

        self._ivy.send_request(
            class_name="ground",
            request_name="CONFIG",
            callback=aircraft_config_callback,
            ac_id=self.id
        )

    def _find_block_name(self, block_id):
        try:
            return next(filter(lambda kv: kv[1] == block_id, self.flight_plan_blocks.items()))[0]
        except StopIteration:
            return None

    def set_values_callback(self, ac_id: int, msg: pl.message.PprzMessage):
        ac_id = int(ac_id)
        if ac_id != self.id:
            return

        for vtype, name, value in zip(msg.fieldtypes, msg.fieldnames, msg.fieldvalues):
            if name in self._observers:
                # Patch before paparazzi/pprzlink#124 is fixed
                if vtype in {'double', 'float'}:
                    value = float(value)
                elif 'int' in vtype:
                    value = int(value)

                old_value = getattr(self, f'_{name}', None)
                if not hasattr(self, f'_{name}') or old_value != value:
                    setattr(self, f'_{name}', value)
                    self.notify_all(
                        name,
                        old_value=old_value,
                        new_value=value
                    )


class AircraftCommands(object):
    def __init__(self, ac: Aircraft):
        self.ac = ac

    def __getattr__(self, item):
        if hasattr(self.ac, item):
            return getattr(self.ac, item)
        else:
            raise AttributeError('No such command \'%s\' available for this aircraft.' % item)

    def _send(self, message):
        return self._ivy.send(message, ac_id=self.id)

    def jump_to_block(self, block_name_or_id):
        if isinstance(int, block_name_or_id):
            block_id = block_name_or_id
        elif isinstance(str, block_name_or_id):
            if block_name_or_id not in self.flight_plan_blocks:
                raise ValueError('No \'%s\' block found, check if the plan is down linked' % block_name_or_id)
            block_id = self.flight_plan_blocks[block_name_or_id]
        else:
            raise TypeError("Expected 'block_name_or_id' to be a string or an integer, found '%s'" %
                            str(type(block_name_or_id)))

        m = pl.message.PprzMessage("ground", "JUMP_TO_BLOCK")
        m['ac_id'] = self.id
        m['block_id'] = block_id

        return self._send(m)

    def takeoff(self):
        # Must ensure takeoff mode is activated before launching
        return self.jump_to_block('Takeoff')

    def launch(self):
        pass

    def change_target_altitude(self, new_altitude):
        m = pl.message.PprzMessage("dl", "DL_SETTING")
        m['index'] = 4  # TODO: fix magic number
        m['value'] = new_altitude

        return self._send(m)
