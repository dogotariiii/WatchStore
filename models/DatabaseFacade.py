from sqlalchemy import select
from db import DatabaseConnector, db
from db_models import User, Watches, Orders


class DatabaseFacade:
    def __init__(self):
        self.connector = DatabaseConnector()

    def fetch_all_watches(self):
        watches_query = select(Watches).filter()
        watches = db.session.execute(watches_query).scalars().all()
        return watches

    def fetch_watch_by_id(self,watch_id):
        watch = db.session.query(Watches).get(watch_id)
        return watch


    def fetch_all_available_watches(self):
        watches_query = select(Watches).filter(Watches.state == 'available')
        watches = db.session.execute(watches_query).scalars().all()
        return watches

    def fetch_all_users(self):
        return db.session.query(User).all()

    def add_user(self, username, email, password, full_name):
        user = User(username=username, email=email, password=password, full_name=full_name)
        self.connector.db.session.add(user)
        self.connector.db.session.commit()

        return user

    def fetch_user_ordered_watches(self, user_id):
        ordered_watches = db.session.query(Orders).filter_by(user_id=user_id).all()
        return ordered_watches

    def fetch_all_ordered_watches(self):
        ordered_watches = db.session.query(Orders).all()
        return ordered_watches

    def delete_bike(self, watch_id):
        watch = db.session.query(Watches).get(watch_id)
        if watch:
            db.session.delete(watch)
            db.session.commit()

    def delete_order(self, order_id):
        order = db.session.query(Orders).get(order_id)
        if order:
            watch_id = order.watch_id

            # Update the status of the watch to 'available'
            watch = db.session.query(Watches).get(watch_id)
            if watch:
                watch.state = 'available'
                db.session.commit()
            else:
                print(f"Watch {watch_id} not found")

            # Delete the order after updating the bike state
            db.session.delete(order)
            db.session.commit()

    def delete_user_by_id(self, user_id):
        user = db.session.query(User).get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    def fetch_order_by_id(self, order_id):
        order = db.session.query(Orders).get(order_id)
        return order

    def delete_watch_by_id(self, watch_id):
        watch = db.session.query(Watches).get(watch_id)
        if watch:
            db.session.delete(watch)
            db.session.commit()

    def fetch_user_by_id(self, user_id):
        user = db.session.query(User).get(user_id)
        return user
