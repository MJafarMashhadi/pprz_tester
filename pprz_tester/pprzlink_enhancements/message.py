from pprzlink.message import PprzMessage


class MessageBuilder:
    def __init__(self, class_name=None, message_name=None, **kwargs):
        self._class_name = class_name
        self._message_name = message_name
        self._payload = dict(kwargs)

    def p(self, payload_name, payload_value):
        self._payload[payload_name] = payload_value
        return self

    def class_name(self, class_name):
        self._class_name = class_name
        return self

    def message_name(self, message_name):
        self._message_name = message_name
        return self

    def build(self):
        m = PprzMessage(self.class_name, self.message_name)
        for k, v in self._payload.items():
            m[k] = v

        return m
