from flight_plan import items
from . import PlanBase


class Example(PlanBase):
    def get_items(self, **kwargs):
        if self.ac.name == 'Microjet':
            plan = [
                items.JumpToBlock('Survey S1-S2'),
                items.WaitForCircles(n_circles=2),
            ]
        elif self.ac.name == 'Bixler':
            plan = [
                items.JumpToBlock('Fly in Square'),
                items.WaitForSeconds(length=15)
            ]
        else:
            plan = []
        plan.append(items.StopTest())
        return plan


Plan = Example
__all__ = ['Plan']
