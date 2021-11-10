from requests import session, codes
from requests.exceptions import ConnectionError, ConnectTimeout

from flask_restx import Resource, abort, fields

from app import api


# Namespace parameters
ns = api.namespace(
    'Retailers',
    description=f'Get list of all retailers available.',
    path='/',
)


# Output
retailer_model = ns.model('RetailerModel', {
    'pid': fields.String(
        description='Personal IDentifier',
        example='hott_pizza',
    ),
    'name': fields.String(
        description='Retailers name',
        example='Hott Pizza',
    ),
    'address': fields.String(
        description='Retailers address',
        example='str. Chezze, 42',
    ),
    'phone': fields.String(
        description='Retailers phone',
        example='123-123-45',
    ),
})


@ns.route('/retailers')
class Retailers(Resource):
    # User (no auth) level access
    @ns.response(503, 'Retailer service is unavailable')
    @ns.marshal_with(retailer_model, code=200, description='List of retailers')
    def get(self):
        '''Get list of retailers'''
        try:
            with session() as s:
                response = s.get('http://localhost:5002/retailers')

                if response.status_code == codes.ok:
                    return response.json()

                abort(response.status_code, **response.json())

        except (ConnectionError, ConnectTimeout):
            abort(503, message='Could not get in touch with retailer service...')
