from select import select
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from app import db
from app.models.transaction import TransactionModel


class ProductModel(db.Model):
    pid = db.Column(db.String(32), primary_key=True)
    section_pid = db.Column(db.String(32), db.ForeignKey('section_model.pid', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    name = db.Column(db.String(32), nullable=False)
    about = db.Column(db.String(64), nullable=False)  # 64 is small, but ok for testing
    price = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)  # Inactive = ppl cant see/buy it

    section = db.relationship('SectionModel', backref='product_model', uselist=False)
    transactions = db.relationship('TransactionModel', backref='product_model', passive_deletes=True)

    # Name and about must be unique *inside* a section
    __table_args__ = (
        db.UniqueConstraint('section_pid', 'name'),
        db.UniqueConstraint('section_pid', 'about'),
    )

    # Easy acces to current stock count
    @hybrid_property
    def in_stock(self):
        return sum(t.amount for t in self.transactions)

    @in_stock.expression
    def in_stock(cls):
        return (
            select([func.sum(TransactionModel.amount)]).
            where(TransactionModel.item_id == cls.id).
            label('in_stock')
        )
