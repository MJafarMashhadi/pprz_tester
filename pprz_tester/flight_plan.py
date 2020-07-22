class PlanItem:
    def __init__(self, matcher=None, actor=None):
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
    def __init__(self, *items):
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
        self.state_id_or_name = state_id_or_name

    def match(self, ac, property_name, old_value, new_value):
        return True

    def act(self, ac, property_name, old_value, new_value):
        ac.commands.jump_to_block(self.state_id_or_name)


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


