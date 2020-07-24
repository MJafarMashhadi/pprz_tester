import collections
import logging
import random
from typing import Dict, Union

import flight_plan
from pprzlink_enhancements import MessageBuilder

logger = logging.getLogger('pprz_tester')

WaypointLocation = collections.namedtuple('WaypointLocation', 'lat long alt')

VALID_RANGE_LAT = [43.4598, 43.4675]
VALID_RANGE_LON = [ 1.2654,  1.2813]
VALID_RANGE_ALT = [250, 300]


def get_rand_lat(): return random.uniform(*VALID_RANGE_LAT)


def get_rand_lon(): return random.uniform(*VALID_RANGE_LON)


def get_rand_alt(): return random.uniform(*VALID_RANGE_ALT)


def get_rand_waypoint(): return WaypointLocation(lat=get_rand_lat(), long=get_rand_lon(), alt=get_rand_alt())


wait_for_mode_2 = [
    flight_plan.PlanItem(
        matcher=lambda _, property_name, __, new_value: property_name == 'pprz_mode__ap_mode' and new_value == 2,
        actor=lambda ac, *_: logger.info(f'Aircraft {ac.id} Mode = AUTO2, ready')
    )
]

takeoff_and_launch = [
    flight_plan.PlanItem(actor=lambda ac, *_: ac.commands.takeoff()),
    flight_plan.WaitForState(state_name_or_id='Takeoff', actor=lambda ac, *_: ac.commands.launch()),
]


def move_waypoints(waypoint_data: Dict[Union[str, int], WaypointLocation]):
    def create_message_callable(wp_id, info):
        def _inner(ac, *_):
            return MessageBuilder('ground', 'MOVE_WAYPOINT') \
                .p('ac_id', ac.id) \
                .p('alt', info.alt) \
                .p('wp_id', str(wp_id)) \
                .p('lat', info.lat) \
                .p('long', info.long) \
                .build()
        return _inner

    return [flight_plan.SendMessage(create_message_callable(wp_id, info)) for wp_id, info in waypoint_data.items()]


def update_waypoints(ac, waypoints):
    fixed_points = dict()
    fuzz_points = dict()

    fuzz_all = False
    for wp_idx, location in waypoints.items():
        if isinstance(wp_idx, int):
            index = wp_idx
        elif wp_idx == '*':
            fuzz_all = True
            continue
        else:
            index = ac.flight_plan_waypoints.get(wp_idx, None)
            if index is None:
                logger.warning(f'Waypoint {wp_idx} not found in the flight plan.')
                continue
        if location is None:
            fuzz_points[index] = get_rand_waypoint()
        else:
            fixed_points[index] = location

    if fuzz_all:
        for wp_idx in ac.flight_plan_waypoints.values() - fixed_points.keys():
            fuzz_points[wp_idx] = get_rand_waypoint()

    return move_waypoints(dict(collections.ChainMap(fixed_points, fuzz_points)))
