
from db import db
from db_models import User, Orders


class UserRepository:
    @staticmethod
    def delete_user(user_id):
        user = db.session.query(User).get(user_id)

        if user:
            # Check if the user has any associated orders
            orders = db.session.query(Orders).filter_by(user_id=user_id).all()

            if orders:
                # If there are associated rentals, delete them first
                for order in orders:
                    db.session.delete(order)

            # Now delete the user
            db.session.delete(user)
            db.session.commit()
            return True
        else:
            return False


class OrderRepository:
    @staticmethod
    def get_orders_by_user(user_id):
        return db.session.query(Orders).filter_by(user_id=user_id).all()
