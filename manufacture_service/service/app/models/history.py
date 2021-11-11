from datetime import datetime

from app import db
from ._aid import Aid


class HistoryModel(db.Model, Aid):
    aid = db.Column(db.String(32), primary_key=True)
    launcher_aid = db.Column(db.String(32), db.ForeignKey('launcher_model.aid', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    datetime = db.Column(db.DateTime, default=datetime.utcnow())

    amount = db.Column(db.Integer, nullable=False)
    success = db.Column(db.Boolean, nullable=False)
    contract = db.Column(db.String(32))

    # send / resived - If some products can be lost on the way to retailer

    def __init__(self, **kwargs):
        db.Model.__init__(self, **kwargs)
        self.aid = self.generate_key(32)
