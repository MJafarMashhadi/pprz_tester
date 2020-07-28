
import flight_plan
from . import PlanBase


class GeneratedCombinationsPlan(PlanBase):
    def get_items(self, **kwargs):
        plan = list()
        i = kwargs.pop('i')
        plan += [
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Wait GPS'),
                flight_plan.WaitForState('Wait GPS'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Geo init'),
                flight_plan.WaitForState('Geo init'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Holding point'),
                flight_plan.WaitForState('Holding point'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Takeoff'),
                flight_plan.WaitForState('Takeoff'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'),
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'),
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'),
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Standby'),
                flight_plan.WaitForState('Standby'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Figure 8 around wp 1'),
                flight_plan.WaitForState('Figure 8 around wp 1'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Oval 1-2'),
                flight_plan.WaitForState('Oval 1-2'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('MOB'),
                flight_plan.WaitForState('MOB'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForState('Survey S1-S2'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Path 1,2,S1,S2,STDBY'),
                flight_plan.WaitForState('Path 1,2,S1,S2,STDBY'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Land Right AF-TD'),
                flight_plan.WaitForState('Land Right AF-TD'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'),
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('Land Left AF-TD'),
                flight_plan.WaitForState('Land Left AF-TD'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
            lambda: [
                flight_plan.JumpToBlock('land'),
                flight_plan.WaitForState('land'),
                flight_plan.JumpToBlock('final'),
                flight_plan.WaitForState('final'), 
            ],
        ][int(i)]()
        plan.append(flight_plan.StopTest())
        return plan


Plan = GeneratedCombinationsPlan
__all__ = ['Plan']
