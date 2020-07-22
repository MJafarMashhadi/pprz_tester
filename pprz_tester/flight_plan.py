from typing import List
import logging

from observer import Observer
logger = logging.getLogger('pprz_tester')
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(logging.StreamHandler())


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

        raise NotImplementedError()
        # return True if finished successfully, return False to keep on queue


class PlanItemOr(PlanItem):
    def __init__(self, *items, **kwargs):
        super(PlanItemOr, self).__init__(**kwargs)
        self.matching_item = None
        self.items = items

    def match(self, *args, **kwargs):
        for idx, item in enumerate(self.items):
            if item.match(*args, **kwargs):
                self.matching_item = idx

    def act(self, *args, **kwargs):
        if not self.matching_item:
            return False

        return self.items[self.matching_item].act(*args, **kwargs)


class PlanItemAnd(PlanItem):
    def __init__(self, *items, **kwargs):
        super(PlanItemAnd, self).__init__(**kwargs)
        self.items = items

    def match(self, *args, **kwargs):
        for idx, item in enumerate(self.items):
            if not item.match(*args, **kwargs):
                return False

        return True

    def act(self, *args, **kwargs):
        success = True
        for item in self.items:
            res = item.act(*args, **kwargs)
            if res is not None and not res:
                success = False

        return success


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

    def act(self, *args, **kwargs):
        if not self.actor:
            return True

        return super(PlanItemWaitForState, self).act(*args, **kwargs)


class PlanItemJumpToState(PlanItem):
    def __init__(self, state_id_or_name, *args, **kwargs):
        super(PlanItemJumpToState, self).__init__(*args, **kwargs)
        self.state_name_or_id = state_id_or_name

    def match(self, ac, property_name, old_value, new_value):
        return True

    def act(self, ac, property_name, old_value, new_value):
        ac.commands.jump_to_block(self.state_name_or_id)


class PlanItemSendMessage(PlanItem):
    def __init__(self, message_builder, *args, **kwargs):
        super(PlanItemSendMessage, self).__init__(*args, **kwargs)
        if not callable(message_builder):
            self.message_builder = lambda *_: message_builder
        else:
            self.message_builder = message_builder

    def act(self, ac, *args):
        message = self.message_builder(ac, *args)
        ac.commands._send(message)


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

