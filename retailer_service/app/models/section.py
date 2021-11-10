from app import db


class SectionModel(db.Model):
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
