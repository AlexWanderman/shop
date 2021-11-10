from flask import Blueprint

models = Blueprint('models', __name__)

from .user import UserModel
from .history import HistoryModel
