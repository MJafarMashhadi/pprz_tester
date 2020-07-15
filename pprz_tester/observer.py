class Observer:
    def __init__(self, ac):
        self.ac = ac

    def __call__(self, property_name, old_value, new_value):
        self.notify(property_name, old_value, new_value)

    def notify(self, property_name, old_value, new_value):
        raise NotImplementedError()