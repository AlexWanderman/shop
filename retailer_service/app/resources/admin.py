from re import match

from flask import g
from flask_restx import Resource, abort, fields

from app import api, auth, db
from app.models import RetailerModel
from app.models.admin import AdminModel


# Namespace
ns = api.namespace(
    'Admins',
    description='Manage admins. ANYONE can create new admins for '
                'demonstration purposes.',
    path='/',
)


# Input
_ = post_admin = ns.parser()
_.add_argument('pid', type=str, required=True, help='Personal IDentifier')
_.add_argument('retailer_pid', type=str, required=True, help='Retailers pid')
_.add_argument('login', type=str, required=True, help='Admins login')
_.add_argument('password', type=str, required=True, help='Admins password')

_ = patch_admin = ns.parser()
_.add_argument('pid', type=str, required=False, help='Personal IDentifier')
_.add_argument('login', type=str, required=False, help='Admins login')
_.add_argument('password', type=str, required=False, help='Admins password')


# Output
admin_model = ns.model('AdminModel', {
    'pid': fields.String(
        description='Personal IDentifier',
        example='admin_main',
    ),
    'retailer_pid': fields.String(
        description='Retailers pid',
        example='hott_pizza',
    ),
    'login': fields.String(
        description='Admins login',
        example='admin_m1',
    ),
})


@ns.route('/admin')
class Admin(Resource):
    _regex = {
        'pid': r'^[a-zA-Z0-9_]{3,32}$',
        'login': r'^[a-zA-Z0-9_]{3,32}$',
        'password': r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?=\S+$).{8,}$',
    }

    # - - - GET - - -
    @auth.login_required
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.marshal_with(admin_model, False, 200, 'Current admin.')
    def get(self):
        '''GET current admin'''
        return g.admin

    # - - - POST - - -
    @ns.expect(post_admin)
    @ns.response(400, 'Invalid input data.')
    @ns.marshal_with(admin_model, False, 201, 'Created admin.')
    def post(self):
        '''POST new admin'''
        args = post_admin.parse_args()

        errors = {}

        if not match(self._regex['pid'], (pid := args['pid'].strip())):
            errors['pid'] = f"Did not match {self._regex['pid']}"

        if not match(self._regex['pid'], (retailer_pid := args['retailer_pid'].strip())):
            errors['retailer_pid'] = f"Did not match {self._regex['pid']}"

        if not match(self._regex['login'], (login := args['login'].strip())):
            errors['login'] = f"Did not match {self._regex['login']}"

        if not match(self._regex['password'], (password := args['password'].strip())):
            errors['password'] = 'Password must have at least one digit, ' +\
                'lowercase and upper letter, a special character (@#$%^&+=) ' +\
                'and not be smaller then 8 symbols'

        if errors:
            abort(400, **errors)

        admin = AdminModel(
            pid=pid,
            retailer_pid=retailer_pid,
            login=login,
            password=password,
        )

        db.session.add(admin)
        db.session.commit()

        return admin

    # - - - PATCH - - -
    @auth.login_required
    @ns.expect(patch_admin)
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(400, 'Invalid input data.')
    @ns.marshal_with(admin_model, False, 200, 'Edited admin.')
    def patch(self):
        '''PATCH admin'''
        args = patch_admin.parse_args()
        admin = AdminModel.query.filter_by(pid=g.admin.pid).first()

        errors = {}

        if (pid := args['pid']) is not None:
            if not match(self._regex['pid'], pid.strip()):
                errors['pid'] = f"Did not match {self._regex['pid']}"

            admin.pid = pid

        if (login := args['login']) is not None:
            if not match(self._regex['login'], login.strip()):
                errors['login'] = f"Did not match {self._regex['login']}"

            admin.login = login

        if (password := args['password']) is not None:
            if not match(self._regex['password'], password.strip()):
                errors['password'] = 'Password must have at least one digit, ' +\
                    'lowercase and upper letter, a special character (@#$%^&+=) ' +\
                    'and not be smaller then 8 symbols'

            admin.password = password

        if errors:
            abort(400, **errors)

        db.session.commit()

        return admin

    # - - - DELETE - - -
    @auth.login_required
    @ns.response(200, 'Done.')
    def delete(self):
        '''DELETE admin'''
        pid = g.admin.pid
        admin = AdminModel.query.filter_by(pid=pid).first()

        db.session.delete(admin)
        db.session.commit()

        return {'message': f'deleted "admin" (pid = {pid})'}
