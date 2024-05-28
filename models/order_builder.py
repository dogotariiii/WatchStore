from abc import ABC, abstractmethod

from db_models import Orders


class Builder(ABC):
    @abstractmethod
    def build(self):
        pass


class OrdersBuilder(Builder):
    def __init__(self, orders=None):
        self.orders = orders if orders else Orders()
        self.decorations = []

    def set_user_id(self, user_id):
        self.orders.user_id = user_id
        return self

    def set_watch_id(self, watch_id):
        self.orders.watch_id = watch_id
        return self

    def set_watch_model(self, watch_model):
        self.orders.watch_model = watch_model
        return self

    def set_watch_name(self, watch_name):
        self.orders.watch_name = watch_name
        return self

    def add_decoration(self, decoration):
        self.decorations.append(decoration)
        return self

    def order_date(self, order_date):
        self.orders.order_date = order_date
        return self

    def set_price(self, price):
        self.orders.price = price
        return self

    def set_total_items(self, total_items):
        self.orders.total_items = total_items
        return self

    def calculate_total_price(self):
        if self.orders.price is None or self.orders.total_items is None:
            raise ValueError("Price per day and rental days must be set before calculating total price")
        self.orders.total_price = self.orders.price * self.orders.total_items
        return self

    @property
    def build(self):
        if not all([self.orders.user_id, self.orders.watch_id, self.orders.order_date, self.orders.price,
                     self.orders.total_price, self.orders.total_items]):
            raise ValueError("All parameters must be set before building Orders")

        new_orders = Orders(user_id=self.orders.user_id)

        return self.orders
