''' Algoritm of sending supply:
    1) Prepare list of retailers and their supply:

        * From LauncherModel:
        [{
            'retailer_pid': 'cheeze_bank',
            'products': {
                'gauda': 30,
                'cheder: 45,
                'parmezan': 33,
            }
        }, ...]

    2) Correct amount for each supply:

        * From HistoryModel:
        2.1) If last attempt for this product was NOT successful - add the last
             attmpted amount (if it < 10_000 just in case) to current amount.

    3) Try to send supply.
'''

from flask import Flask, Blueprint
from flask_restx import Api
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# from manager.app import app as manager
# from manager.app.tasks import simple_task


api_bp = Blueprint('api', __name__)
api = Api(
    api_bp,
    version='0.1',
    title='Manufacture Service API',
    description='Manage manufactures, their admins, their assortment (for '
                'WHO, WHAT and HOW MUCH they send).',
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

    # @app.route('/test_celery/start/<name>')
    # def start_simple_task(name):
    #     task = simple_task.delay()
    #     return task.id

    # @app.route('/test_celery/result/<task_id>')
    # def result_simple_task(task_id):
    #     task = simple_task.AsyncResult(task_id)
    #     result = task.get(timeout=3)
    #     response = {
    #         'state': task.state,
    #         'result': result,
    #     }
    #     return response

    return app
