from flask import Blueprint

resources = Blueprint('resources', __name__)

from .retailer import RetailerRead, RetailerChange
from .admin import Admin
from .section import SectionRead, SectionChange
from .product import ProductRead, ProductChange
from .retail import Contract, Import
