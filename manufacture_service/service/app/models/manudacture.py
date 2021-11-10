from app import db


class ManufactureModel(db.Model):
    pid = db.Column(db.String(32), primary_key=True)

    name = db.Column(db.String(32), unique=True, nullable=False)
    address = db.Column(db.String(64), unique=True, nullable=False)
    phone = db.Column(db.String(32), unique=True, nullable=False)

    admins = db.relationship('AdminModel', backref='manufacture_model', passive_deletes=True)
