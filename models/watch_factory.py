from abc import abstractmethod, ABC

from db_models import Watches


class Factory(ABC):
    @abstractmethod
    def create(self, name, model, case_material, dial_color, price, image_url):
        pass


class WatchFactory(Factory):
    def create(self, name, model, case_material, dial_color, price, image_url):
        if not all([name, model, case_material, dial_color, price, image_url]):
            raise ValueError("Incomplete watch information. Make sure all attributes are set.")

        # Create and return a new Watches object
        return Watches(
            name=name,
            model=model,
            case_material=case_material,
            dial_color=dial_color,
            price=price,
            image_url=image_url
        )


