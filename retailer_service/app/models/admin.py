from flask import g
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, auth


class AdminModel(db.Model):
    pid = db.Column(db.String(32), primary_key=True)
    retailer_pid = db.Column(db.String(32), db.ForeignKey('retailer_model.pid', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    login = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

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
        admin = AdminModel.query.filter_by(login=login).first()

        if not admin or not admin.check_password(password):
            return False

        g.admin = admin
        return True
