import flight_plan
from . import PlanBase


class Example(PlanBase):
    def get_items(self, **kwargs):
        if self.ac.name == 'Microjet':
            plan = [
                flight_plan.JumpToBlock('Survey S1-S2'),
                flight_plan.WaitForCircles(n_circles=2),
            ]
        elif self.ac.name == 'Bixler':
            plan = [
                flight_plan.JumpToBlock('Fly in Square'),
                flight_plan.WaitForSeconds(length=15)
            ]
        else:
            plan = []
        plan.append(flight_plan.StopTest())
        return plan


Plan = Example
__all__ = ['Plan']
