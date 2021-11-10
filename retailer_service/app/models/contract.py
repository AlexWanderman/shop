from datetime import datetime

from app import db
from ._aid import Aid


class ContractModel(db.Model, Aid):
    aid = db.Column(db.String(32), primary_key=True)
    retailer_pid = db.Column(db.String(32), db.ForeignKey('retailer_model.pid', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    pay_method = db.Column(db.String(32))
    datetime = db.Column(db.DateTime, default=datetime.utcnow())

    transactions = db.relationship('TransactionModel', backref='contact_model', passive_deletes=True)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)
        self.aid = self.generate_key(32)

    @staticmethod
    def get_pay_methods():
        return ('online', 'google_pay', 'apple_pay', 'yandex_money', 'cash')
