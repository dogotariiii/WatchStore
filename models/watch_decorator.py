from abc import abstractmethod, ABC

from models import Watch


class WatchDecorator(Watch, ABC):
    def __init__(self, watch):
        self.watch = watch

    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def price(self):
        pass


class SpareStrap(WatchDecorator):
    def __init__(self, watch):
        super().__init__(watch)

    def description(self):
        return f"{super().description()}, Spare Strap: Yes"

    def price(self):
        return self.watch.price() + self.watch.price() * 0.20


class Case(WatchDecorator):
    def __init__(self, watch):
        super().__init__(watch)

    def description(self):
        return f"{super().description()}, Case: Yes"

    def price(self):
        return self.watch.price() + 35


class GiftBox(WatchDecorator):
    def __init__(self, watch):
        super().__init__(watch)

    def description(self):
        return f"{super().description()}, Gift Box: Yes"

    def price(self):
        return self.watch.price() + 14
