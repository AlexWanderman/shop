from datetime import datetime

from flask import g
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, auth


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(32), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(80), unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    datetime_join = db.Column(db.DateTime, default=datetime.utcnow())

    @property
    def password(self):
        return None

    @password.setter
    def password(self, password):
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_login(cls, login):
        return cls.query.filter_by(login=login).first()

    @staticmethod
    @auth.verify_password
    def verify_password(login, password):
        user = UserModel.query.filter_by(login=login).first()

        if not user or not user.check_password(password):
            return False

        g.user = user
        return True
