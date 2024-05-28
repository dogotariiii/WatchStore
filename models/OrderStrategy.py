from abc import ABC, abstractmethod

class OrderStrategy(ABC):
    @abstractmethod
    def calculate_order(self, total_items, item_price):
        pass

class StandardOrderStrategy(OrderStrategy):
    def calculate_order(self, total_items, item_price):
        return total_items * item_price + 20

class FreeShippingOrderStrategy(OrderStrategy):
    def calculate_order(self, total_items, item_price):
        return total_items * item_price