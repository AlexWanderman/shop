from flask import Flask, Blueprint
from flask_restx import Api
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

api_bp = Blueprint('api', __name__)
api = Api(
    api_bp,
    version='0.1',
    title='Shop Service API',
    description='Manage users. Read lists of retailers, their sections and '
                'products. Buy products.',
)
auth = HTTPBasicAuth()
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import models
    from app.resources import resources

    app.register_blueprint(models)
    app.register_blueprint(resources)
    app.register_blueprint(api_bp)

    return app
