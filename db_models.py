from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase

from db import db


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100))
    registration_date = db.Column(db.TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    last_login = db.Column(db.TIMESTAMP)
    is_admin = db.Column(db.Boolean, default=False)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


class Watches(Base):
    __tablename__ = "watches"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    model = db.Column(db.String(50))
    case_material = db.Column(db.String(50))
    dial_color = db.Column(db.String(50))
    price = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    state = db.Column(db.Enum('available', 'sold', name='watch_state'), default='available')

    def sold_out(self):
        self.state = 'sold'


class Orders(Base):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id_user'), nullable=False)
    user_fullname = db.Column(db.String(50), nullable=True)
    watch_id = db.Column(db.Integer, db.ForeignKey('watches.id'), nullable=False)
    watch_model = db.Column(db.String(50), nullable=False)
    watch_name = db.Column(db.String(100), nullable=False)
    decorations = db.Column(db.String(255), nullable=True)
    order_date = db.Column(db.TIMESTAMP, nullable=True)
    price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    total_items = db.Column(db.Integer, nullable=False)
    # Define relationships using string-based references
    watch = db.relationship('Watches', backref=db.backref('orders', lazy=True))
    user = db.relationship('User', backref=db.backref('orders', lazy=True))


