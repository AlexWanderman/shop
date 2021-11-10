from flask import Blueprint

resources = Blueprint('resources', __name__)

from .user import User
from .retailers import Retailers
from .sections import Sections
from .products import Products
from .buy import Buy
from .history import History, Contract
