from flask import g
from flask_restx import Resource, fields, reqparse

from app import api, auth, db
from app.models import UserModel

ns = api.namespace('user', description='User manipulation.', path='/')


_ = create_user_args = reqparse.RequestParser(bundle_errors=True)
_.add_argument('login', type=str, help='User login', required=True)
_.add_argument('password', type=str, help='User password', required=True)
_.add_argument('email', type=str, help='User email', required=True)
_.add_argument('first_name', type=str, help='User first name', required=True)
_.add_argument('last_name', type=str, help='User last name', required=True)

_ = edit_user_args = reqparse.RequestParser(bundle_errors=True)
_.add_argument('login', type=str, help='User login')
_.add_argument('password', type=str, help='User password')
_.add_argument('email', type=str, help='User email')
_.add_argument('first_name', type=str, help='User first name')
_.add_argument('last_name', type=str, help='User last name')


user_model = api.model('UserModel', {
    'id': fields.Integer(required=True, description='Item identifier', example=1),
    'login': fields.String(required=True, description='User login', example='new_user_111'),
    'email': fields.String(required=True, description='User email', example='user@mail.com'),
    'first_name': fields.String(required=True, description='User first name', example='Jacob'),
    'last_name': fields.String(required=True, description='User last name', example='Thomas'),
    'datetime_join': fields.DateTime(required=True, description='The date and time user created account', example='2000-01-01T01:00:00.000Z'),
})


@ns.route('/user')
class User(Resource):
    # @ns.doc(params=user_parameters)
    @ns.expect(create_user_args)
    @ns.response(401, description='Invalid or missing user credentials')
    @ns.response(400, 'Invalid args provided')
    @ns.marshal_with(user_model, code=201, description='User created')
    def post(self):
        '''Creates a new user'''
        args = create_user_args.parse_args()

        user = UserModel(
            login=args['login'],
            password=args['password'],
            email=args['email'],
            first_name=args['first_name'],
            last_name=args['last_name'],
        )

        db.session.add(user)
        db.session.commit()

        return user, 201

    @auth.login_required
    @ns.response(401, description='Invalid or missing user credentials')
    @ns.marshal_with(user_model)
    def get(self):
        '''Returns the current user'''
        return g.user

    @auth.login_required
    # @ns.doc(params=user_parameters)
    @ns.expect(edit_user_args)
    @ns.response(401, description='Invalid or missing user credentials')
    @ns.marshal_with(user_model)
    def patch(self):
        '''Updates the current user.'''
        args = edit_user_args.parse_args()

        if args['login'] is not None:
            g.user.login = args['login']

        if args['password'] is not None:
            g.user.password = args['password']

        if args['email'] is not None:
            g.user.email = args['email']

        if args['first_name'] is not None:
            g.user.first_name = args['first_name']

        if args['last_name'] is not None:
            g.user.last_name = args['last_name']

        db.session.commit()
        return g.user

    @auth.login_required
    @ns.response(401, description='Invalid or missing user credentials')
    @ns.response(200, description='User was deleted succesfuly.')
    def delete(self):
        '''Deletes the current user '''
        db.session.delete(g.user)
        db.session.commit()
        return {'message': 'done'}
