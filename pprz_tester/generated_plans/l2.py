
import flight_plan
import flight_plan_generator
from . import PlanBase


class GeneratedCombinationsPlan(PlanBase):
    def get_items(self, **kwargs):
        plan = list()
        i = kwargs.pop('i')
        new_wp_locs = {
        }
        if new_wp_locs:
            plan += flight_plan_generator.move_waypoints(new_wp_locs)
        plan += [
            lambda: [  # 0
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.WaitForSeconds(68),
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.WaitForSeconds(67),
            ],
            lambda: [  # 1
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.WaitForSeconds(58),
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.WaitForSeconds(50),
            ],
            lambda: [  # 2
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.WaitForSeconds(51),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.WaitForSeconds(68),
            ],
            lambda: [  # 3
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.WaitForSeconds(61),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForSeconds(51),
            ],
            lambda: [  # 4
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.WaitForSeconds(52),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.WaitForSeconds(53),
            ],
            lambda: [  # 5
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.WaitForSeconds(68),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'),
                flight_plan.WaitForSeconds(65),
            ],
            lambda: [  # 6
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.WaitForSeconds(54),
                flight_plan.JumpToBlock('HOME'),
                flight_plan.WaitForState('HOME'),
                flight_plan.WaitForSeconds(68),
            ],
            lambda: [  # 7
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.WaitForSeconds(56),
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.WaitForSeconds(67),
            ],
            lambda: [  # 8
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.WaitForSeconds(53),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.WaitForSeconds(69),
            ],
            lambda: [  # 9
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.WaitForSeconds(68),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForSeconds(54),
            ],
            lambda: [  # 10
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.WaitForSeconds(65),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.WaitForSeconds(55),
            ],
            lambda: [  # 11
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.WaitForSeconds(53),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'),
                flight_plan.WaitForSeconds(63),
            ],
            lambda: [  # 12
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.WaitForSeconds(62),
                flight_plan.JumpToBlock('HOME'),
                flight_plan.WaitForState('HOME'),
                flight_plan.WaitForSeconds(59),
            ],
            lambda: [  # 13
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.WaitForSeconds(56),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.WaitForSeconds(65),
            ],
            lambda: [  # 14
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.WaitForSeconds(56),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForSeconds(64),
            ],
            lambda: [  # 15
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.WaitForSeconds(68),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.WaitForSeconds(58),
            ],
            lambda: [  # 16
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.WaitForSeconds(50),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'),
                flight_plan.WaitForSeconds(60),
            ],
            lambda: [  # 17
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.WaitForSeconds(68),
                flight_plan.JumpToBlock('HOME'),
                flight_plan.WaitForState('HOME'),
                flight_plan.WaitForSeconds(55),
            ],
            lambda: [  # 18
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.WaitForSeconds(51),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForSeconds(66),
            ],
            lambda: [  # 19
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.WaitForSeconds(68),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.WaitForSeconds(54),
            ],
            lambda: [  # 20
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.WaitForSeconds(54),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'),
                flight_plan.WaitForSeconds(62),
            ],
            lambda: [  # 21
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.WaitForSeconds(55),
                flight_plan.JumpToBlock('HOME'),
                flight_plan.WaitForState('HOME'),
                flight_plan.WaitForSeconds(58),
            ],
            lambda: [  # 22
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForSeconds(53),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.WaitForSeconds(69),
            ],
            lambda: [  # 23
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForSeconds(51),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'),
                flight_plan.WaitForSeconds(61),
            ],
            lambda: [  # 24
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForSeconds(56),
                flight_plan.JumpToBlock('HOME'),
                flight_plan.WaitForState('HOME'),
                flight_plan.WaitForSeconds(65),
            ],
            lambda: [  # 25
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.WaitForSeconds(55),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'),
                flight_plan.WaitForSeconds(60),
            ],
            lambda: [  # 26
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.WaitForSeconds(65),
                flight_plan.JumpToBlock('HOME'),
                flight_plan.WaitForState('HOME'),
                flight_plan.WaitForSeconds(58),
            ],
            lambda: [  # 27
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'),
                flight_plan.WaitForSeconds(65),
                flight_plan.JumpToBlock('HOME'),
                flight_plan.WaitForState('HOME'),
                flight_plan.WaitForSeconds(66),
            ],
        ][int(i)]()
        plan.append(flight_plan.StopTest())
        return plan


Plan = GeneratedCombinationsPlan
__all__ = ['Plan']
