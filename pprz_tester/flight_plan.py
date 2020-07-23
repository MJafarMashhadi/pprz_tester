import logging
import math
from typing import List

from observer import Observer

logger = logging.getLogger('pprz_tester')


class PlanItem:
    def __init__(self, *, matcher=None, actor=None):
        self.matcher = matcher
        self.actor = actor

    def match(self, ac, property_name, old_value, new_value):
        if self.matcher:
            return self.matcher(ac, property_name, old_value, new_value)

        return True

    def act(self, ac, property_name, old_value, new_value):
        if self.actor:
            return self.actor(ac, property_name, old_value, new_value)

        return True


class PlanItemAny(PlanItem):
    def __init__(self, *items, **kwargs):
        super(PlanItemAny, self).__init__(**kwargs)
        self.matching_item = None
        self.items = items

    def match(self, *args, **kwargs):
        self.matching_item = None
        for idx, item in enumerate(self.items):
            if item.match(*args, **kwargs):
                self.matching_item = idx
                return True
        return False

    def act(self, *args, **kwargs):
        if not self.matching_item:
            return False

        return self.items[self.matching_item].act(*args, **kwargs)

    def __str__(self):
        return '<Flight plan combo:' + ' | '.join(str(item) for item in self.items) + '>'


class PlanItemAll(PlanItem):
    def __init__(self, *items, **kwargs):
        super(PlanItemAll, self).__init__(**kwargs)
        self.all_items = items
        self.remaining_items = list(items)

    def match(self, *args, **kwargs):
        fulfilled = list()
        for idx, item in enumerate(self.remaining_items):
            if item.match(*args, **kwargs):
                fulfilled.append(idx)

        for idx in reversed(fulfilled):
            self.remaining_items.pop(idx)

        return len(self.remaining_items) == 0

    def act(self, *args, **kwargs):
        success = True
        for item in self.all_items:
            res = item.act(*args, **kwargs)
            if res is not None and not res:
                success = False

        return success

    def __str__(self):
        return '<Flight plan combo:' + ' & '.join(str(item) for item in self.all_items) + '>'


class PlanItemWaitForState(PlanItem):
    def __init__(self, state_name_or_id, *args, **kwargs):
        super(PlanItemWaitForState, self).__init__(*args, **kwargs)
        self.state_name_or_id = state_name_or_id

    def match(self, ac, property_name, old_value, new_value):
        if property_name == 'navigation':
            new_state_id = new_value['cur_block']
        elif property_name == 'navigation__cur_block':
            new_state_id = new_value
        else:
            return False

        if isinstance(self.state_name_or_id, str):
            new_state_name = ac.find_block_name(new_state_id)
            state_name = self.state_name_or_id
            return state_name == new_state_name
        else:
            state_id = self.state_name_or_id
            return state_id == new_state_id

    def __str__(self):
        return f'<Flight plan item: wait for state {self.state_name_or_id}>'


class PlanItemJumpToBlock(PlanItem):
    def __init__(self, state_id_or_name, *args, **kwargs):
        super(PlanItemJumpToBlock, self).__init__(*args, **kwargs)
        self.state_name_or_id = state_id_or_name

    def act(self, ac, property_name, old_value, new_value):
        ac.commands.jump_to_block(self.state_name_or_id)

    def __str__(self):
        return f'<Flight plan item: go to state {self.state_name_or_id}>'


class PlanItemSendMessage(PlanItem):
    def __init__(self, message_builder, *args, **kwargs):
        super(PlanItemSendMessage, self).__init__(*args, **kwargs)
        if not callable(message_builder):
            def create_message_builder_callable(message_builder):
                def _inner(*_):
                    return message_builder

                return _inner

            self.message_builder = create_message_builder_callable(message_builder)
        else:
            self.message_builder = message_builder

    def act(self, ac, *args):
        message = self.message_builder(ac, *args)
        ac.commands._send(message)

    def __str__(self):
        return f'<Flight plan item: send ivy message>'


class PlanItemWaitForCircles(PlanItem):
    def __init__(self, n_circles=0, *args, **kwargs):
        super(PlanItemWaitForCircles, self).__init__(*args, **kwargs)
        self.n_circles = n_circles

    def match(self, ac, property_name, old_value, new_value):
        if property_name == 'navigation':
            new_value = new_value['circle_count']
        elif property_name == 'navigation__circle_count':
            new_value = new_value
        else:
            return False

        return new_value >= self.n_circles

    def __str__(self):
        return f'<Flight plan item: wait for {self.n_circles} circles>'


class PlanItemWaitClimb(PlanItem):
    def __init__(self, tolerance=5, *args, **kwargs):
        super(PlanItemWaitClimb, self).__init__(*args, **kwargs)
        self.tolerance = tolerance
        self.last_value = None

    def match(self, ac, property_name, old_value, new_value):
        if property_name == 'flight_param':
            old_value = self.last_value
            new_alt = new_value['alt']
            self.last_value = new_alt
        else:
            return False

        return old_value is not None \
           and math.fabs(old_value - new_alt) < self.tolerance \
           and math.fabs(new_value['climb']) < (self.tolerance / 10.)

    def __str__(self):
        return f'<Flight plan item: wait until altitude stabilizes, tolerance={self.tolerance}m>'


class FlightPlanPerformingObserver(Observer):
    def __init__(self, ac, plan_items=list()):
        super(FlightPlanPerformingObserver, self).__init__(ac)
        self._plan: List[PlanItem] = list(plan_items)

    @property
    def plan(self):
        return self._plan

    def notify(self, property_name, old_value, new_value):
        while self._plan:
            next_item = self._plan[0]
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
                    plan_item = self._plan.pop(0)
                    logger.info(f'Performed a flight plan item, {plan_item}, remaining items={len(self._plan)}')
                else:
                    logger.error(f'Failed to perform a flight plan item, keeping the item on the queue.')
                    break
