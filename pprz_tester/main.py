import sys

from flight_plan import PlanItemWaitForState, PlanItemAnd, PlanItemJumpToState, \
    FlightPlanPerformingObserver, PlanItemWaitClimb
from flight_plan_generator import move_waypoints, WaypointLocation, takeoff_and_launch, wait_for_mode_2, \
    VALID_RANGE_LAT, VALID_RANGE_LON
from flight_recorder import RecordFlight

sys.path.append("../pprzlink/lib/v1.0/python")
import logging
from typing import Dict
import datetime
import random

import pprzlink as pl

from pprz_tester.pprzlink_enhancements import IvySubscribe
from pprz_tester import aircraft

logger = logging.getLogger('pprz_tester')
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())

agent_name = "MJafarIvyAgent"
start_time = datetime.datetime.now().strftime("%m%d-%H%M%S")
ivy = pl.ivy.IvyMessagesInterface(
    agent_name=agent_name,
    start_ivy=True,
)

aircraft_list: Dict[int, aircraft.Aircraft] = dict()


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

    oval_alt = random.uniform(250, 300)
    survey_alt = random.uniform(250, 300)
    def get_rand_lat(): return random.uniform(*VALID_RANGE_LAT)
    def get_rand_lon(): return random.uniform(*VALID_RANGE_LON)

    set_up = wait_for_mode_2 + takeoff_and_launch + move_waypoints({
        # 3: WaypointLocation(lat=43.4659053, long=1.2700005, alt=300),
        # 4: WaypointLocation(lat=43.4654170, long=1.2799074, alt=300),
        3: WaypointLocation(lat=get_rand_lat(), long=get_rand_lon(), alt=oval_alt),  # 1
        4: WaypointLocation(lat=get_rand_lat(), long=get_rand_lon(), alt=oval_alt),  # 2
        6: WaypointLocation(lat=get_rand_lat(), long=get_rand_lon(), alt=survey_alt),  # S1
        7: WaypointLocation(lat=get_rand_lat(), long=get_rand_lon(), alt=survey_alt),  # S2
    }) + [
        PlanItemAnd(
            PlanItemWaitForState(state_name_or_id='Standby', actor=lambda *_: None),
            # PlanItemWaitForCircles(n_circles=1, actor=lambda *_: None),
            PlanItemWaitClimb(tolerance=5),
        ),
    ]

    flight_plan_runner = FlightPlanPerformingObserver(new_ac, set_up + [
        PlanItemJumpToState(state_id_or_name='Oval 1-2'),
    ])
    new_ac.observe('navigation__cur_block', flight_plan_runner)
    new_ac.observe('navigation__circle_count', flight_plan_runner)
    new_ac.observe('pprz_mode__ap_mode', flight_plan_runner)
    new_ac.observe('flight_param', flight_plan_runner)
    new_ac.observe('flight_param', RecordFlight(new_ac))

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
    import time
    time.sleep(0.1)  # TOFF
    request_aircraft_list()


if __name__ == '__main__':
    main()
