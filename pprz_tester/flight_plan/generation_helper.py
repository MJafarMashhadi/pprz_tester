import collections
import logging
from typing import Dict, Union

from observer import Observer
from pprzlink_enhancements import MessageBuilder
from . import items
from .waypoint import WaypointLocation, get_rand_waypoint

logger = logging.getLogger('pprz_tester')

wait_for_mode_2 = [
    items.PlanItem(
        matcher=lambda _, property_name, __, new_value: property_name == 'pprz_mode__ap_mode' and new_value == 2,
        actor=lambda ac, *_: logger.info(f'Aircraft {ac.id} Mode = AUTO2, ready')
    )
]

takeoff_and_launch = [
    items.PlanItem(actor=lambda ac, *_: ac.commands.takeoff()),
    items.WaitForState(state_name_or_id='Takeoff', actor=lambda ac, *_: ac.commands.launch()),
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

    return [items.SendMessage(create_message_callable(wp_id, info)) for wp_id, info in waypoint_data.items()]


def prepare_new_waypoint_locations(flight_plan_waypoints, waypoints):
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
            index = flight_plan_waypoints.get(wp_idx, None)
            if index is None:
                logger.warning(f'Waypoint {wp_idx} not found in the flight plan.')
                continue
        if location is None:
            fuzz_points[index] = get_rand_waypoint()
        else:
            fixed_points[index] = location

    if fuzz_all:
        for wp_idx in flight_plan_waypoints.values() - fixed_points.keys():
            fuzz_points[wp_idx] = get_rand_waypoint()

    return dict(collections.ChainMap(fixed_points, fuzz_points))


class FlightPlanPerformingObserver(Observer):
    def __init__(self, ac, plan_generator):
        super(FlightPlanPerformingObserver, self).__init__(ac)
        self._plan = plan_generator
        self._next_item = None

    def notify(self, property_name, old_value, new_value):
        while True:
            if not self._next_item:
                try:
                    self._next_item = next(self._plan)  # Pop next item
                    logger.debug(f'Next plan item: {self._next_item}')
                except StopIteration:
                    self._next_item = None
                    break
            next_item = self._next_item
            if not next_item.match(self.ac, property_name, old_value, new_value):
                break

            act_successful = False
            try:
                act_successful = next_item.act(self.ac, property_name, old_value, new_value)
            except:
                act_successful = False
                import traceback
                traceback.print_exc()
            finally:
                if act_successful is None or act_successful:
                    self._next_item = None  # In next iteration next will be called on the iterator
                    plan_item = next_item
                    logger.info(f'Performed {plan_item}')
                else:
                    logger.error(f'Failed to perform {next_item}, keeping the item on the queue.')
                    break
