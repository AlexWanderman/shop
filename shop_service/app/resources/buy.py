from requests import session, codes
from requests.exceptions import ConnectionError, ConnectTimeout

from flask import g, request
from flask_restx import Resource, abort

from app import api, auth, db
from app.models import HistoryModel


# Namespace parameters
ns = api.namespace(
    'Buy',
    description=f'Create buy requests,',
    path='/',
)


# Input
_ = post_buy = ns.parser()
_.add_argument('retailer_pid', type=str, required=True, help='Retailers pid')
_.add_argument('products', type=dict[str, int], required=True, help='Retailers pid')
# products -> {product_pid: amount, ...}
_.add_argument('pay_method', type=str, required=True, help='Pay method')


@ns.route('/buy')
class Buy(Resource):
    @auth.login_required
    @ns.response(401, description='Invalid or missing user credentials')
    @ns.response(201, description='Buy request was succesful.')
    def post(self):
        '''Send a buy request to retailer service'''
        try:
            with session() as s:
                response = s.post(f'http://localhost:5002/buy', json=request.json)

                if response.status_code == 200:
                    data = response.json()

                    cheque = HistoryModel(
                        user_id=g.user.id,
                        contract=data['contract_aid'],
                    )

                    db.session.add(cheque)
                    db.session.commit()

                    return data

                abort(response.status_code, **response.json())

        except (ConnectionError, ConnectTimeout):
            abort(503, message='Could not get in touch with retailer service...')
