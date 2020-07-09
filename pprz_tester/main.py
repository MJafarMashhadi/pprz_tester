import sys

sys.path.append("../pprzlink/lib/v1.0/python")
import logging
from typing import Dict

import pprzlink as pl

from ivy_subscribe import IvySubscribe
import aircraft

logger = logging.getLogger('pprz_tester')
logger.setLevel(logging.DEBUG)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())

agent_name = "MJafarIvyAgent"

ivy = pl.ivy.IvyMessagesInterface(
    agent_name=agent_name,
    start_ivy=True,
)

aircraft_list: Dict[int, aircraft.Aircraft] = dict()


class Observer:
    def __init__(self, ac):
        self.ac = ac

    def __call__(self, property_name, old_value, new_value):
        self.notify(property_name, old_value, new_value)

    def notify(self, property_name, old_value, new_value):
        raise NotImplementedError()


class CurrentBlockChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        logger.info(f'Aircraft {self.ac.id} in block {new_value}: {self.ac._find_block_name(new_value)}')


class APModeChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        logger.debug(f'{self.ac.id} changed mode to {new_value}')
        if self.ac._ap_mode == 2:  # AUTO1 or AUTO2
            logger.info(f'Aircraft {self.ac.id} Mode = AUTO2, ready')
            self.ac.commands.takeoff()


class CircleCountChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        logger.debug(f'{self.ac.id} circle count changed to {new_value}')


class AltitudeChanged(Observer):
    def notify(self, property_name, old_value, new_value):
        if old_value is not None and abs(old_value - new_value) < 0.5:
            # Not large enough, just ignore.
            return
        logger.debug(f'Aircraft {self.ac.id} changed altitude to {new_value}m')


def add_aircraft_if_new(ac_id, kwargs):
    if ac_id not in aircraft_list:
        new_ac = create_aircraft(ac_id, kwargs)
        aircraft_list[ac_id] = new_ac


def create_aircraft(ac_id, kwargs):
    new_ac = aircraft.Aircraft(
        ivy_link=ivy,
        ac_id=ac_id,
        **kwargs
    )
    new_ac.observe('cur_block', CurrentBlockChanged(new_ac))
    new_ac.observe('ap_mode', APModeChanged(new_ac))
    new_ac.observe('circle_count', CircleCountChanged(new_ac))
    new_ac.observe('alt', AltitudeChanged(new_ac))
    return new_ac


@IvySubscribe(ivy_link=ivy, message_types=[("ground", "NEW_AIRCRAFT")])
def new_aircraft_callback(ac_id, msg):
    logger.info(f"New aircraft message {ac_id}: {msg}")
    ac_id = int(ac_id)
    kwargs = dict(auto_request_config=True)
    add_aircraft_if_new(ac_id, kwargs)


def request_aircraft_list():
    def aircraft_list_callback(ac_id, msg):
        for ac_id in map(int, msg['ac_list']):
            kwargs = dict(auto_request_config=True)
            add_aircraft_if_new(ac_id, kwargs)

    ivy.send_request(
        class_name="ground",
        request_name="AIRCRAFTS",
        callback=aircraft_list_callback,
    )


def main():
    request_aircraft_list()


if __name__ == '__main__':
    main()
