from app import db
from ._aid import Aid


class LauncherModel(db.Model, Aid):
    aid = db.Column(db.String(32), primary_key=True)
    manufacture_pid = db.Column(db.String(32), db.ForeignKey('manufacture_model.pid', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    retailer_pid = db.Column(db.String(80), nullable=False)
    product_pid = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)

    __table_args__ = (db.UniqueConstraint('retailer_pid', 'product_pid'), )

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)
        self.aid = self.generate_key(32)
