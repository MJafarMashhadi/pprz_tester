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


def add_arcraft_if_new(ac_id, kwargs):
    if ac_id not in aircraft_list:
        aircraft_list[ac_id] = aircraft.Aircraft(
            ivy_link=ivy,
            ac_id=ac_id,
            **kwargs
        )


@IvySubscribe(ivy_link=ivy, message_types=[("ground", "NEW_AIRCRAFT")])
def new_aircraft_callback(ac_id, msg):
    logger.info(f"New aircraft message {ac_id}: {msg}")
    ac_id = int(ac_id)
    kwargs = dict(auto_request_config=True)
    add_arcraft_if_new(ac_id, kwargs)


def request_aircraft_list():
    def aircraft_list_callback(ac_id, msg):
        for ac_id in map(int, msg['ac_list']):
            kwargs = dict(auto_request_config=True)
            add_arcraft_if_new(ac_id, kwargs)

    ivy.send_request(
        class_name="ground",
        request_name="AIRCRAFTS",
        callback=aircraft_list_callback,
    )


def main():
    request_aircraft_list()


if __name__ == '__main__':
    main()
