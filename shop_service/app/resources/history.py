from requests import codes, request, session
from requests.exceptions import ConnectionError, ConnectTimeout

from flask import g
from flask_restx import Resource, abort, fields

from app import api, auth
from app.models import HistoryModel

# Namespace parameters
ns = api.namespace(
    'History',
    description=f'Shopping history of user',
    path='/',
)


# Output
history_model = ns.model('HistoryModel', {
    'id': fields.Integer(
        description='ID',
        example=1,
    ),
    'contract': fields.String(
        description='Contract aid (aotomatic id: str)',
        example='OLockoddcA1aW1yRxcygUB0tatAo1rk5',
    ),
})


contract_model = ns.model('ContractModel (external)', {
    'aid': fields.String(
        description='Automatic IDentifier',
        example='summer_sail',
    ),
    'retailer_pid': fields.String(
        description='Retailers pid',
        example='hott_pizza',
    ),
    'pay_method': fields.String(
        description='Pay method',
        example='cash/google_pay/apple_pay/yandex_money...',
    ),
    'datetime': fields.DateTime(
        description='Date and time of contract.',
        example='2020-10-10 05:05:25.000000',
    ),
    'transactions': fields.Raw,
})


@ns.route('/history')
class History(Resource):
    @auth.login_required
    @ns.response(401, description='Invalid or missing user credentials')
    @ns.marshal_with(history_model, True, 200, 'List of all contacts (chequecs).')
    def get(self):
        '''History of users shopping'''
        return HistoryModel.query.filter_by(user_id=g.user.id).all()


@ns.route('/history/<contact_aid>')
class Contract(Resource):
    @auth.login_required
    @ns.response(401, 'Invalid or missing user credentials')
    @ns.response(404, 'Contact not found.')
    @ns.marshal_with(contract_model)
    def get(self, contact_aid):
        '''Detailed shopping contract (cheque)'''
        try:
            with session() as s:
                response = s.get(f'http://localhost:5002/contract/{contact_aid}')

                if response.status_code == 200:
                    return response.json()

                if response.status_code == 404:
                    abort(404, 'Contact not found.')

                abort(response.status_code, **response.json())

        except (ConnectionError, ConnectTimeout):
            abort(503, message='Could not get in touch with retailer service...')
