from flask import Blueprint

models = Blueprint('models', __name__)

# Personal IDentifier (can be set to whatever String(32))
# pid = db.Column(db.String(32), primary_key=True)
# ..._pid = db.Column(db.String(32), db.ForeignKey('... .pid'), nullable=False)

# Automatic IDentifier (generates by DB)
# aid = db.Column(db.String(32), primary_key=True)
# ..._aid = db.Column(db.String(32), db.ForeignKey('... .aid'), nullable=False)

# This order is important!

from .retailer import RetailerModel
from .admin import AdminModel              # r RetailerModel <-- a AdminModel
from .section import SectionModel          # r RetailerModel <-- s SectionModel
from .product import ProductModel          # r RetailerModel <-- s SectionModel <-- p ProductModel
from .contract import ContractModel        # r RetailerModel <-- c ContractModel
from .transaction import TransactionModel  # c ContractModel <-- t TransactionModel --> p ProductModel
