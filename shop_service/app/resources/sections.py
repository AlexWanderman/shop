from requests import session, codes
from requests.exceptions import ConnectionError, ConnectTimeout

from flask_restx import Resource, abort, fields

from app import api


# Namespace parameters
ns = api.namespace(
    'Sections',
    description=f'Get list of all sections available of the retailer.',
    path='/',
)


# Output
section_model = ns.model('SectionModel', {
    'pid': fields.String(
        description='Personal IDentifier',
        example='summer_sail',
    ),
    'retailer_pid': fields.String(
        description='Retailers pid',
        example='hott_pizza',
    ),
    'name': fields.String(
        description='Sections name',
        example='Summer sail',
    ),
    'about': fields.String(
        description='Some info about section',
        example='Limited offer for ...',
    ),
    'is_active': fields.Boolean(
        description='Can it be accessed by all',
        example=True,
    ),
})


@ns.route('/sections/<retailer_pid>')
class Sections(Resource):
    @ns.response(503, 'Retailer service is unavailable.')
    @ns.marshal_with(section_model, code=200, description='List of retailer sections.')
    def get(self, retailer_pid):
        '''Get list of all retailer sections'''
        try:
            with session() as s:
                response = s.get(f'http://localhost:5002/sections/{retailer_pid}')

                if response.status_code == codes.ok:
                    return response.json()

                abort(response.status_code, **response.json())

        except (ConnectionError, ConnectTimeout):
            abort(503, message='Could not get in touch with retailer service...')
