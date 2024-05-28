# models/watch.py
import copy


class Watch:
    def __init__(self):
        self.name = None
        self.model = None
        self.case_material = None
        self.dial_color = None
        self.price = None
        self.image_url = None

    def clone(self):
        return copy.deepcopy(self)
