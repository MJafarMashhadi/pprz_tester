import logging

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
        self.mode = None
        self.current_block = None
        self.flight_plan_blocks = dict()

        if auto_request_config:
            self.request_config()

        self._ac = AircraftCommands(self)
        # TODO: find a better way to use the decorator instead of patching like this. It defeats the purpose.
        self._update_mode_callback = IvySubscribe(ivy_link=self._ivy, message_types=[("telemetry", "PPRZ_MODE")])\
            (self._update_mode_callback)
        self._navigation_callback = IvySubscribe(ivy_link=self._ivy, message_types=[("telemetry", "NAVIGATION")])\
            (self._navigation_callback)

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

    def update_mode(self, msg):
        new_mode = int(msg['ap_mode'])
        if new_mode == self.mode:
            # No news
            return False
        self.mode = new_mode
        if self.mode == 2:  # AUTO1 or AUTO2
            print(f'{self.id} Mode = AUTO2, ready')

        return True

    def _update_mode_callback(self, ac_id: int, msg: pl.message.PprzMessage):
        ac_id = int(ac_id)
        if ac_id != self.id:
            return

        mode_changed = self.update_mode(msg)
        if mode_changed:
            logger.debug(f'{ac_id} changed mode to {msg}')

    def _find_block_name(self, block_id):
        return next(filter(lambda kv: kv[1] == block_id, self.flight_plan_blocks.items()))[0]

    def update_navigation_block(self, msg: pl.message.PprzMessage):
        block_id = int(msg['cur_block'])
        if block_id == self.current_block:
            return False

        self.current_block = block_id
        print(f'{self.id}: in a new block: {self._find_block_name(block_id)}')
        return True

    def _navigation_callback(self, ac_id: int, msg: pl.message.PprzMessage):
        ac_id = int(ac_id)
        if ac_id != self.id:
            return

        self.update_navigation_block(msg)


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
