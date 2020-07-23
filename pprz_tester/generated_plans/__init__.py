class PlanBase:
    def __init__(self, ac):
        self.ac = ac

    def get_items(self, **kwargs):
        raise NotImplementedError()
