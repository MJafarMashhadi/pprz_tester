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
            3: WaypointLocation(lat=43.4659053, long=1.27, alt=300.0),
            4: WaypointLocation(lat=43.465417, long=1.2799074, alt=300.0),
        }
        if new_wp_locs:
            plan += generation_helper.move_waypoints(new_wp_locs)
        plan_blocks = [
            lambda: [  # 0
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(76),
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(74),
            ],
            lambda: [  # 1
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(89),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(75),
            ],
            lambda: [  # 2
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(79),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(86),
            ],
            lambda: [  # 3
                items.JumpToBlock('Figure 8 around wp 1'),
                items.WaitForState('Figure 8 around wp 1'),
                items.WaitForSeconds(61),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(65),
            ],
            lambda: [  # 4
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(73),
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(79),
            ],
            lambda: [  # 5
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(68),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(77),
            ],
            lambda: [  # 6
                items.JumpToBlock('Oval 1-2'),
                items.WaitForState('Oval 1-2'),
                items.WaitForSeconds(73),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(78),
            ],
            lambda: [  # 7
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(70),
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(85),
            ],
            lambda: [  # 8
                items.JumpToBlock('MOB'),
                items.WaitForState('MOB'),
                items.WaitForSeconds(68),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(75),
            ],
            lambda: [  # 9
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForState('Survey S1-S2'),
                items.WaitForSeconds(62),
                items.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                items.WaitForState('Path 1,2,S1,S2,STDBY'),
                items.WaitForSeconds(88),
            ],
        ][int(i)]()
        permutation = int(permutation)
        block_size = 3
        max_permutations = 1
        for n in range(len(plan_blocks) // block_size, 0, -1):
            max_permutations *= n
        if permutation >= max_permutations:
            raise ValueError(f'Max number of permutations for this scenario is {max_permutations}')
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
