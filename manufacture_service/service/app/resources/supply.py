from re import match
from requests import session
from requests.exceptions import ConnectionError, ConnectTimeout
from json import dump

from flask import g
from flask_restx import Resource, abort, fields

from app import api, auth, db
from app.models.launcher import LauncherModel
from app.models.history import HistoryModel


# Namespace
ns = api.namespace(
    'Launcher',
    description='Manage manufacturers list of supplies for each retailer',
    path='/',
)


# TODO Reed all history for selected launcher


@ns.route('/supply/<retailer_pid>')
class Supply(Resource):
    @auth.login_required
    @ns.response(401, 'Invalid or missing auth.')
    @ns.response(403, 'Admin-Launcher manufacture mistmatch.')
    @ns.response(404, 'Launcher not found.')
    @ns.response(200, 'Done.')
    def post(self, retailer_pid):
        # list: product_pid and amount
        launcher = LauncherModel.query.filter_by(
            manufacture_pid=g.admin.manufacture_pid,
            retailer_pid=retailer_pid,
            is_active=True,
        ).all()

        if not launcher:
            abort(404, 'Launcher with this retailer not found.')

        success = False
        contract = None

        try:
            with session() as s:
                data = {
                    "retailer_pid": retailer_pid,
                    "products": {},
                }

                for n in launcher:
                    # TODO УЧИТЫВАТЬ НЕУДАЧНЫЕ ПОПЫТКИ
                    history = HistoryModel.query.filter_by(
                        launcher_aid=n.aid,
                    ).order_by(
                        -HistoryModel.aid,
                    ).first()

                    if history is None or history.success:
                        data['products'][n.product_pid] = n.amount
                    else:
                        data['products'][n.product_pid] = n.amount + history.amount

                response = s.post(f'http://localhost:5002/import', json=data)

                if response.status_code == 200:
                    r_data = response.json()

                    success = True
                    contract = r_data['contract_aid']

                    return {'contract_aid': contract}

                abort(response.status_code, **response.json())

        except (ConnectionError, ConnectTimeout):
            abort(503, message='Could not get in touch with retailer service...')
        finally:
            for n in launcher:
                db.session.add(HistoryModel(
                    launcher_aid=n.aid,
                    amount=data['products'][n.product_pid],
                    success=success,
                    contract=contract,
                ))

            db.session.commit()
