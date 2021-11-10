from app import db


class HistoryModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('user_model.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    contract = db.Column(db.String(80))
