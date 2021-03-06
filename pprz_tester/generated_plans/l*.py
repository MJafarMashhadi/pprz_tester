
from flight_plan import items
from flight_plan import generation_helper
from flight_plan.waypoint import WaypointLocation
from . import PlanBase

import itertools


class GeneratedCombinationsPlan(PlanBase):
    def get_items(self, **kwargs):
        plan = list()
        i = kwargs.pop('i')
        permutation = kwargs.pop('permutation', 0)
        new_wp_locs = {
            3: WaypointLocation(lat=43.4659053, long=1.27, alt=280.0),
            4: WaypointLocation(lat=43.465417, long=1.2799074, alt=280.0),
        }
        if new_wp_locs:
            plan += generation_helper.move_waypoints(new_wp_locs)
        plan_blocks = [
            lambda: [  # 0
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(86),
            ],
            lambda: [  # 1
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(60),
            ],
            lambda: [  # 2
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(84),
            ],
            lambda: [  # 3
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(73),
            ],
            lambda: [  # 4
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(86),
            ],
            lambda: [  # 5
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(62),
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(67),
            ],
            lambda: [  # 6
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(71),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(82),
            ],
            lambda: [  # 7
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(70),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(61),
            ],
            lambda: [  # 8
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(69),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(84),
            ],
            lambda: [  # 9
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(61),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(73),
            ],
            lambda: [  # 10
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(78),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(65),
            ],
            lambda: [  # 11
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(82),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(82),
            ],
            lambda: [  # 12
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(84),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(66),
            ],
            lambda: [  # 13
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(64),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(76),
            ],
            lambda: [  # 14
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(70),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(78),
            ],
            lambda: [  # 15
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(61),
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(69),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(86),
            ],
            lambda: [  # 16
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(89),
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(84),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(60),
            ],
            lambda: [  # 17
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(76),
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(83),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(67),
            ],
            lambda: [  # 18
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(69),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(60),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(64),
            ],
            lambda: [  # 19
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(66),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(80),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(89),
            ],
            lambda: [  # 20
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(84),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(61),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(89),
            ],
            lambda: [  # 21
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(60),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(78),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(67),
            ],
            lambda: [  # 22
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(89),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(60),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(83),
            ],
            lambda: [  # 23
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(60),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(88),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(79),
            ],
            lambda: [  # 24
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(61),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(64),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(62),
            ],
            lambda: [  # 25
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(67),
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(79),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(75),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(65),
            ],
            lambda: [  # 26
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(89),
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(72),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(64),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(70),
            ],
            lambda: [  # 27
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(72),
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(83),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(75),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(65),
            ],
            lambda: [  # 28
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(62),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(69),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(83),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(85),
            ],
            lambda: [  # 29
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(66),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(81),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(82),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(70),
            ],
            lambda: [  # 30
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(78),
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(86),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(86),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(60),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(66),
            ],
        ][int(i)]()
        permutation = int(permutation)
        block_size = 3
        max_permutations = 1
        for n in range(len(plan_blocks) // block_size, 0, -1):
            max_permutations *= n
        if permutation >= max_permutations:
            # ValueError(f'Max number of permutations for this scenario is {max_permutations}')
            print(f'Max number of permutations for this scenario is {max_permutations}')
            return [items.StopTest()]
        if permutation > 0:
            blocks = []
            for i in range(0, len(plan_blocks), block_size):
                blocks.append(plan_blocks[i:i + block_size])
            for i, perm in enumerate(itertools.permutations(blocks)):
                if i == permutation:
                    plan_blocks = list(itertools.chain(*perm))
                    break
            else:
                raise ValueError('Invalid permutation')
        plan += plan_blocks

        return plan


Plan = GeneratedCombinationsPlan
__all__ = ['Plan']
