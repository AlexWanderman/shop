from app import db
from ._aid import Aid


class TransactionModel(db.Model, Aid):
    aid = db.Column(db.String(32), primary_key=True)

    product_pid = db.Column(db.Integer, db.ForeignKey('product_model.pid', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    product = db.relationship('ProductModel', backref='transaction_model', viewonly=True)

    contract_aid = db.Column(db.Integer, db.ForeignKey('contract_model.aid', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    contract = db.relationship('ContractModel', backref='transaction_model', viewonly=True)

    sold_at = db.Column(db.Integer, default=None)
    amount = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)
        self.aid = self.generate_key(32)
