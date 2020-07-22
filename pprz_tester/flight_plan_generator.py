import logging
from collections import namedtuple
from typing import Dict, Union

from flight_plan import PlanItemSendMessage, PlanItemWaitForState, PlanItem
from pprzlink_enhancements import MessageBuilder

logger = logging.getLogger('pprz_tester')
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())

WaypointLocation = namedtuple('WaypointLocation', 'lat long alt')

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
    return [PlanItemSendMessage(lambda ac, *_: MessageBuilder('ground', 'MOVE_WAYPOINT')
                                .p('ac_id', ac.id)
                                .p('alt', info.alt)
                                .p('wp_id', str(wpid))
                                .p('lat', info.lat)
                                .p('long', info.long)
                                .build())
            for wpid, info in waypoint_data.items()]
