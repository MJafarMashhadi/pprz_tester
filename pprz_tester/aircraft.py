import logging
import re
from collections import defaultdict
from typing import Callable, Any, Dict

from lxml import etree

import pprzlink as pl
from pprzlink_enhancements import IvySubscribe, MessageBuilder

logger = logging.getLogger('pprz_tester')


class AircraftParameters:
    def __init__(self, ac):
        self.ac = ac
        self.values: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(lambda: None))

    @staticmethod
    def _is_ac_param(name):
        return re.match(r'[a-z_]+__[\w_]+', name)

    def __getattr__(self, item):
        if not self._is_ac_param(item):
            raise AttributeError(f'Parameter \'{item}\' not found.')

        msg_class, param_name = item.split('__')
        if msg_class in self.values and self.values[msg_class] and param_name not in self.values[msg_class]:
            raise AttributeError(f'Parameter {param_name} is not found in {msg_class}. '
                                 f'Known valid parameters are {", ".join(self.values[msg_class].keys())}')

        val = self.values[msg_class][param_name]
        return val

    def __setattr__(self, key, value):
        if not self._is_ac_param(key):
            return super(AircraftParameters, self).__setattr__(key, value)

        msg_class, param_name = key.split('__')
        self.values[msg_class][param_name] = value


class Aircraft(object):
    def __init__(self,
                 ivy_link: pl.ivy.IvyMessagesInterface,
                 ac_id: int,
                 auto_request_config: bool = True
                 ):
        self._ivy = ivy_link
        self.id = ac_id
        self.flight_plan_uri = None
        self.airframe_settings_uri = None
        self.name = None
        self.flight_plan_blocks = dict()
        self.setting_items = dict()
        self._observers = defaultdict(list)
        self._params = AircraftParameters(self)

        if auto_request_config:
            self.request_config()

        self._ac = AircraftCommands(self)
        # TODO: find a better way to use the decorator instead of patching like this. It defeats the purpose.
        self.set_values_callback = IvySubscribe(ivy_link=self._ivy, message_types=[
            ("telemetry", "PPRZ_MODE"),
            ("telemetry", "NAVIGATION"),
            ("telemetry", "COMMANDS"),
            ("ground", "FLIGHT_PARAM"),
            ("ground", "ENGINE_STATUS"),
            ("ground", "CIRCLE_STATUS"),
            ("ground", "WAYPOINT_MOVED"),
        ])(self.set_values_callback)

    def observe(self, property_name: str, callback: Callable[[str, Any, Any], None]):
        self._observers[property_name].append(callback)

    def look_away(self, property_name: str, callback: Callable[[str, Any, Any], None]):
        self._observers[property_name].remove(callback)

    def _notify_all(self, name: str, *, old_value: Any, new_value: Any):
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

    @property
    def params(self):
        return self._params

    def __str__(self):
        return f'Aircraft <id={self.id}, name={self.name}, loaded_fp={self.flight_plan_uri is not None}>'

    def request_config(self):
        def aircraft_config_callback(ac_id, msg):
            assert int(ac_id) == self.id

            logger.info(f"Got new aircraft config {ac_id}: {msg}")
            self.flight_plan_uri = msg['flight_plan']
            self.airframe_settings_uri = msg['settings']
            self.name = msg['ac_name']

            logger.info(f"Loading flight plan {ac_id}: {self.flight_plan_uri}")
            fp_tree = etree.parse(self.flight_plan_uri)
            for block in fp_tree.xpath("//block"):
                self.flight_plan_blocks[block.attrib['name']] = int(block.attrib['no'])

            logger.info(f"Loading settings {ac_id}: {self.airframe_settings_uri}")
            settings_tree = etree.parse(self.airframe_settings_uri)
            for order, settings_item in enumerate(settings_tree.xpath('//dl_setting')):
                name = settings_item.attrib['var']
                values = dict(settings_item.attrib)
                values.pop('var')
                values['order'] = order
                self.setting_items[name] = values

        self._ivy.send_request(
            class_name="ground",
            request_name="CONFIG",
            callback=aircraft_config_callback,
            ac_id=self.id
        )

    def find_block_name(self, block_id):
        try:
            return next(filter(lambda kv: kv[1] == block_id, self.flight_plan_blocks.items()))[0]
        except StopIteration:
            return None

    def set_values_callback(self, ac_id: int, msg: pl.message.PprzMessage):
        ac_id = int(ac_id)
        if ac_id != self.id:
            return

        # Patch before paparazzi/pprzlink#124 is fixed
        for vtype, fieldname, value in zip(msg.fieldtypes, msg.fieldnames, msg.fieldvalues):
            modifier = lambda V: V
            if vtype in {'double', 'float'}:
                modifier = float
            elif 'int' in vtype:
                modifier = int
            if '[' in vtype and 'char' not in vtype:
                _modifier = modifier
                modifier = lambda V: [_modifier(X) for X in V]

            msg[fieldname] = modifier(value)

        for fieldname, value in zip(msg.fieldnames, msg.fieldvalues):
            name = f'{msg.name.lower()}__{fieldname}'
            old_value = getattr(self.params, name, None)
            if old_value != value:
                setattr(self.params, name, value)
                self._notify_all(
                    name,
                    old_value=old_value,
                    new_value=value
                )
        self._notify_all(
            msg.name.lower(),
            old_value=None,
            new_value=msg
        )

    def __del__(self):
        self._observers.clear()
        self.set_values_callback.__ivy_subs__.unsubscribe()


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

    def _send_setting_update(self, setting_name, setting_value):
        return self._send(
            MessageBuilder(class_name="ground", message_name="DL_SETTING")
            .p('ac_id', self.ac.id)
            .p('index', self.setting_items[setting_name]['order'])
            .p('value', setting_value)
            .build()
        )

    def jump_to_block(self, block_name_or_id):
        if isinstance(block_name_or_id, int):
            block_id = block_name_or_id
            block_name = self.ac.find_block_name(block_id)
        elif isinstance(block_name_or_id, str):
            if block_name_or_id not in self.flight_plan_blocks:
                raise ValueError('No \'%s\' block found, check if the plan is down linked' % block_name_or_id)
            block_name = block_name_or_id
            block_id = self.flight_plan_blocks[block_name]
        else:
            raise TypeError("Expected 'block_name_or_id' to be a string or an integer, found '%s'" %
                            str(type(block_name_or_id)))

        logger.info(f'Aircraft {self.id} is going to jump to block {block_id}: {block_name}')

        return self._send(
            MessageBuilder(class_name="ground", message_name="JUMP_TO_BLOCK")
            .p('ac_id', self.id)
            .p('block_id', block_id)
            .build()
        )

    def takeoff(self):
        # Must ensure takeoff mode is activated before launching
        return self.jump_to_block('Takeoff')

    def launch(self):
        return self._send_setting_update(setting_name='autopilot.launch', setting_value=1)

    def change_target_altitude(self, new_altitude):
        return self._send_setting_update(setting_name='flight_altitude', setting_value=new_altitude)
