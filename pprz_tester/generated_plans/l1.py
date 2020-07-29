from flight_plan import items
from flight_plan import generation_helper
from flight_plan.waypoint import WaypointLocation
from . import PlanBase


class GeneratedCombinationsPlan(PlanBase):
    def get_items(self, **kwargs):
        plan = list()
        i = kwargs.pop('i')
        new_wp_locs = {
            3: WaypointLocation(lat=43.4659053, long=1.27, alt=300.0),
            4: WaypointLocation(lat=43.465417, long=1.2799074, alt=300.0),
        }
        if new_wp_locs:
            plan += generation_helper.move_waypoints(new_wp_locs)
        plan += [
            lambda: [  # 0
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(57),
            ],
            lambda: [  # 1
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(63),
            ],
            lambda: [  # 2
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(62),
            ],
            lambda: [  # 3
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(56),
            ],
            lambda: [  # 4
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(63),
            ],
            lambda: [  # 5
                items.JumpToBlock('Land Right AF-TD'),
                items.WaitForState('Land Right AF-TD'),
                items.WaitForSeconds(65),
            ],
            lambda: [  # 6
                items.JumpToBlock('Land Left AF-TD'),
                items.WaitForState('Land Left AF-TD'),
                items.WaitForSeconds(51),
            ],
            lambda: [  # 7
                items.JumpToBlock('HOME'),
                items.WaitForState('HOME'),
                items.WaitForSeconds(53),
            ],
        ][int(i)]()
        plan.append(items.StopTest())
        return plan


Plan = GeneratedCombinationsPlan
__all__ = ['Plan']
