from flask import Blueprint

models = Blueprint('models', __name__)

from .manudacture import ManufactureModel
from .admin import AdminModel
from .launcher import LauncherModel
from .history import HistoryModel
