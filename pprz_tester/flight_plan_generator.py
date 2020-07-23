import logging
import random
from collections import namedtuple
from typing import Dict, Union

from flight_plan import PlanItemSendMessage, PlanItemWaitForState, PlanItem
from pprzlink_enhancements import MessageBuilder

logger = logging.getLogger('pprz_tester')

WaypointLocation = namedtuple('WaypointLocation', 'lat long alt')

VALID_RANGE_LAT = [43.4598, 43.4675]
VALID_RANGE_LON = [ 1.2654,  1.2813]


def get_rand_lat(): return random.uniform(*VALID_RANGE_LAT)


def get_rand_lon(): return random.uniform(*VALID_RANGE_LON)


wait_for_mode_2 = [
    PlanItem(
        matcher=lambda _, property_name, __, new_value: property_name == 'pprz_mode__ap_mode' and new_value == 2,
        actor=lambda ac, *_: logger.info(f'Aircraft {ac.id} Mode = AUTO2, ready')
    )
]

takeoff_and_launch = [
    PlanItem(actor=lambda ac, *_: ac.commands.takeoff()),
    PlanItemWaitForState(state_name_or_id='Takeoff', actor=lambda ac, *_: ac.commands.launch()),
]


def move_waypoints(waypoint_data: Dict[Union[str, int], WaypointLocation]):
    def create_message_callable(wpid, info):
        def _inner(ac, *_):
            return MessageBuilder('ground', 'MOVE_WAYPOINT') \
                .p('ac_id', ac.id) \
                .p('alt', info.alt) \
                .p('wp_id', str(wpid)) \
                .p('lat', info.lat) \
                .p('long', info.long) \
                .build()
        return _inner

    return [PlanItemSendMessage(create_message_callable(wpid, info)) for wpid, info in waypoint_data.items()]


