from flask import Blueprint

resources = Blueprint('resources', __name__)

from .manufacture import ManufactureRead, ManufactureChange
from .admin import Admin
