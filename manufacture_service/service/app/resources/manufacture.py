from re import match

from flask import g
from flask_restx import Resource, abort, fields

from app import api, auth, db
from app.models import ManufactureModel


# Namespace
ns = api.namespace(
    'Manufactures',
    description='Get list of all manufactures, or manage one. And yes, ANYONE '
                'can create new manufactures (and admins as well) for '
                'demonstration purposes.',
    path='/',
)


# Input
_ = post_manufacture = ns.parser()
_.add_argument('pid', type=str, required=True, help='Personal IDentifier')
_.add_argument('name', type=str, required=True, help='Manufactures name')
_.add_argument('address', type=str, required=True, help='Manufactures address')
_.add_argument('phone', type=str, required=True, help='Manufactures phone')

_ = patch_manufacture = ns.parser()
_.add_argument('pid', type=str, required=False, help='Personal IDentifier')
_.add_argument('name', type=str, required=False, help='Manufactures name')
_.add_argument('address', type=str, required=False, help='Manufactures address')
_.add_argument('phone', type=str, required=False, help='Manufactures phone')


# Output
manufacture_model = ns.model('ManufactureModel', {
    'pid': fields.String(
        description='Personal IDentifier',
        example='hott_pizza',
    ),
    'name': fields.String(
        description='Manufactures name',
        example='Hott Pizza',
    ),
    'address': fields.String(
        description='Manufactures address',
        example='str. Chezze, 42',
    ),
    'phone': fields.String(
        description='Manufactures phone',
        example='123-123-45',
    ),
})


@ns.route('/manufactures')
class ManufactureRead(Resource):
    # - - - GET - - -
    @ns.marshal_with(manufacture_model, True, 200, 'List of manufactures.')
    def get(self):
        '''GET list of all manufactures'''
        return ManufactureModel.query.all()


@ns.route('/manufacture')
class ManufactureChange(Resource):
    _regex = {
        'pid': r'^[a-zA-Z0-9_]{3,32}$',
        'name': r'^[\w\d ]{3,32}$',
        'address': r'.{3,64}',
        'phone': r'^\d{3}-\d{3}-\d{2}$',
    }

    # - - - POST - - -
    @ns.expect(post_manufacture)
    @ns.response(400, 'Invalid input data.')
    @ns.marshal_with(manufacture_model, False, 201, 'Created manufacture.')
    def post(self):
        '''POST new manufacture'''
        args = post_manufacture.parse_args()

        errors = {}

        if not match(self._regex['pid'], (pid := args['pid'].strip())):
            errors['pid'] = f"Did not match {self._regex['pid']}"

        if not match(self._regex['name'], (name := args['name'].strip())):
            errors['name'] = f"Did not match {self._regex['name']}"

        if not match(self._regex['address'], (address := args['address'].strip())):
            errors['address'] = f"Did not match {self._regex['address']}"

        if not match(self._regex['phone'], (phone := args['phone'].strip())):
            errors['phone'] = f"Did not match {self._regex['phone']}"

        if errors:
            abort(400, **errors)

        manufacture = ManufactureModel(
            pid=pid,
            name=name,
            address=address,
            phone=phone,
        )

        db.session.add(manufacture)
        db.session.commit()

        return manufacture

    # - - - PATCH - - -
    @auth.login_required
    @ns.expect(patch_manufacture)
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(400, 'Invalid input data.')
    @ns.marshal_with(manufacture_model, False, 200, 'Edited manufacture.')
    def patch(self):
        '''PATCH manufacture'''
        args = patch_manufacture.parse_args()
        manufacture = ManufactureModel.query.filter_by(pid=g.admin.manufacture_pid).first()

        errors = {}

        if (pid := args['pid']) is not None:
            if not match(self._regex['pid'], pid.strip()):
                errors['pid'] = f"Did not match {self._regex['pid']}"

            manufacture.pid = pid

        if (name := args['name']) is not None:
            if not match(self._regex['name'], name.strip()):
                errors['name'] = f"Did not match {self._regex['name']}"

            manufacture.name = name

        if (address := args['address']) is not None:
            if not match(self._regex['address'], address.strip()):
                errors['address'] = f"Did not match {self._regex['address']}"

            manufacture.address = address

        if (phone := args['phone']) is not None:
            if not match(self._regex['phone'], phone.strip()):
                errors['phone'] = f"Did not match {self._regex['phone']}"

            manufacture.phone = phone

        if errors:
            abort(400, **errors)

        db.session.commit()

        return manufacture

    # - - - DELETE - - -
    @auth.login_required
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(200, 'Done.')
    def delete(self):
        '''DELETE manufacture'''
        pid = g.admin.manufacture_pid
        manufacture = ManufactureModel.query.filter_by(pid=pid).first()

        db.session.delete(manufacture)
        db.session.commit()

        return {'message': f'deleted "manufacture" (pid = {pid})'}
