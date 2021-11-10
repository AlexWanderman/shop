from requests import session, codes
from requests.exceptions import ConnectionError, ConnectTimeout

from flask_restx import Resource, abort, fields

from app import api


# Namespace parameters
ns = api.namespace(
    'Products',
    description=f'Get list of all products available of the retailer.',
    path='/',
)


# Output
product_model = ns.model('ProductModel', {
    'pid': fields.String(
        description='Personal IDentifier',
        example='spicy_dune',
    ),
    'section_pid': fields.String(
        description='Sections pid',
        example='summer_sail',
    ),
    'name': fields.String(
        description='Products name',
        example='Spicy Dune',
    ),
    'about': fields.String(
        description='Some info about product',
        example='Big slice of ...',
    ),
    'price': fields.Integer(
        description='Products price',
        example=15,
    ),
    'in_stock': fields.Integer(
        description='How much product is in stock',
        example=38,
    ),
})


@ns.route('/products/<section_pid>')
class Products(Resource):
    @ns.response(503, 'Retailer service is unavailable.')
    @ns.marshal_with(product_model)
    def get(self, section_pid):
        '''Get list of all retailer products'''
        try:
            with session() as s:
                response = s.get(f'http://localhost:5002/products/{section_pid}')

                if response.status_code == codes.ok:
                    return response.json()

                abort(response.status_code, **response.json())

        except (ConnectionError, ConnectTimeout):
            abort(503, message='Could not get in touch with retailer service...')
