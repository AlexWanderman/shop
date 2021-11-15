from app import db


class SectionModel(db.Model):
    # PID as a primary key must be unique, but from the logic perspective
    # it should be unique only for a particular retailer. For examle:
    # retailer_a and ratiler_b should be able to both have summer_sale. One
    # way to make this happen is to utilise composite primary key, but this
    # might complicate the system too much, so I choose left it this wasy
    # for now.

    pid = db.Column(db.String(32), primary_key=True)
    retailer_pid = db.Column(db.String(32), db.ForeignKey('retailer_model.pid', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)

    name = db.Column(db.String(32), nullable=False)
    about = db.Column(db.String(64), nullable=False)  # 64 is small, but ok for testing
    is_active = db.Column(db.Boolean, nullable=False)  # Inactive = ppl cant see it and its products

    products = db.relationship('ProductModel', backref='section_model', passive_deletes=True, lazy='dynamic')

    # Name and about must be unique *inside* a retailer
    __table_args__ = (
        db.UniqueConstraint('retailer_pid', 'name'),
        db.UniqueConstraint('retailer_pid', 'about'),
    )
