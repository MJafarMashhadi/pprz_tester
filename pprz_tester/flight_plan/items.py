import logging
import math
import time

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


class WaitAny(PlanItem):
    def __init__(self, *items, **kwargs):
        super(WaitAny, self).__init__(**kwargs)
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


class WaitAll(PlanItem):
    def __init__(self, *items, **kwargs):
        super(WaitAll, self).__init__(**kwargs)
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


class WaitForState(PlanItem):
    def __init__(self, state_name_or_id, *args, **kwargs):
        super(WaitForState, self).__init__(*args, **kwargs)
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


class WaitForSpeed(PlanItem):
    def __init__(self, target_speed, tolerance=0.5, *args, **kwargs):
        super(WaitForSpeed, self).__init__(*args, **kwargs)
        self.target_speed = target_speed
        self.tolerance = tolerance

    def match(self, ac, property_name, old_value, new_value):
        return math.fabs(ac.params.flight_param__airspeed - self.target_speed) <= self.tolerance


class JumpToBlock(PlanItem):
    def __init__(self, state_id_or_name, *args, **kwargs):
        super(JumpToBlock, self).__init__(*args, **kwargs)
        self.state_name_or_id = state_id_or_name

    def act(self, ac, property_name, old_value, new_value):
        ac.commands.jump_to_block(self.state_name_or_id)

    def __str__(self):
        return f'<Flight plan item: go to state {self.state_name_or_id}>'


class SendMessage(PlanItem):
    def __init__(self, message_builder, *args, **kwargs):
        super(SendMessage, self).__init__(*args, **kwargs)
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


class WaitForCircles(PlanItem):
    def __init__(self, n_circles=0, *args, **kwargs):
        super(WaitForCircles, self).__init__(*args, **kwargs)
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


class WaitClimb(PlanItem):
    def __init__(self, tolerance=5, *args, **kwargs):
        super(WaitClimb, self).__init__(*args, **kwargs)
        self.tolerance = tolerance
        self.last_value = None

    def match(self, ac, property_name, old_value, new_value):
        if property_name == 'flight_param':
            old_value = self.last_value
            new_alt = new_value['agl']
            self.last_value = new_alt
        else:
            return False

        return old_value is not None \
               and math.fabs(old_value - new_alt) < self.tolerance \
               and math.fabs(new_value['climb']) < (self.tolerance / 10.)

    def __str__(self):
        return f'<Flight plan item: wait until altitude stabilizes, tolerance={self.tolerance}m>'


class StopTest(PlanItem):
    def act(self, ac, property_name, old_value, new_value):
        import os
        import signal
        os.kill(os.getpid(), signal.SIGINT)

    def __str__(self):
        return '<Flight plan item: stop test>'


class WaitForSeconds(PlanItem):
    _now = time.time

    def __init__(self, length, *args, **kwargs):
        self.first_encounter = None
        self.length = length
        super(WaitForSeconds, self).__init__(*args, **kwargs)

    def match(self, *args, **kwargs):
        super(WaitForSeconds, self).match(*args, **kwargs)
        if self.first_encounter is None:
            self.first_encounter = self._now()

        return self._now() - self.first_encounter >= self.length

    def __str__(self):
        return f'<Flight plan item: wait for {self.length} seconds>'
