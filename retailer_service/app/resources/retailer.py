from re import match

from flask import g
from flask_restx import Resource, abort, fields

from app import api, auth, db
from app.models import RetailerModel


# Namespace
ns = api.namespace(
    'Retailers',
    description='Get list of all retailers, or manage one. And yes, ANYONE '
                'can create new retailers (and admins as well) for '
                'demonstration purposes.',
    path='/',
)


# Input
_ = post_retailer = ns.parser()
_.add_argument('pid', type=str, required=True, help='Personal IDentifier')
_.add_argument('name', type=str, required=True, help='Retailers name')
_.add_argument('address', type=str, required=True, help='Retailers address')
_.add_argument('phone', type=str, required=True, help='Retailers phone')

_ = patch_retailer = ns.parser()
_.add_argument('pid', type=str, required=False, help='Personal IDentifier')
_.add_argument('name', type=str, required=False, help='Retailers name')
_.add_argument('address', type=str, required=False, help='Retailers address')
_.add_argument('phone', type=str, required=False, help='Retailers phone')


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
class RetailerRead(Resource):
    # - - - GET - - -
    @ns.marshal_with(retailer_model, True, 200, 'List of retailers.')
    def get(self):
        '''GET list of all retailers'''
        return RetailerModel.query.all()


@ns.route('/retailer')
class RetailerChange(Resource):
    _regex = {
        'pid': r'^[a-zA-Z0-9_]{3,32}$',
        'name': r'^[\w\d ]{3,32}$',
        'address': r'.{3,64}',
        'phone': r'^\d{3}-\d{3}-\d{2}$',
    }

    # - - - POST - - -
    @ns.expect(post_retailer)
    @ns.response(400, 'Invalid input data.')
    @ns.marshal_with(retailer_model, False, 201, 'Created retailer.')
    def post(self):
        '''POST new retailer'''
        args = post_retailer.parse_args()

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

        retailer = RetailerModel(
            pid=pid,
            name=name,
            address=address,
            phone=phone,
        )

        db.session.add(retailer)
        db.session.commit()

        return retailer

    # - - - PATCH - - -
    @auth.login_required
    @ns.expect(patch_retailer)
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(400, 'Invalid input data.')
    @ns.marshal_with(retailer_model, False, 200, 'Edited retailer.')
    def patch(self):
        '''PATCH retailer'''
        args = patch_retailer.parse_args()
        retailer = RetailerModel.query.filter_by(pid=g.admin.retailer_pid).first()

        errors = {}

        if (pid := args['pid']) is not None:
            if not match(self._regex['pid'], pid.strip()):
                errors['pid'] = f"Did not match {self._regex['pid']}"

            retailer.pid = pid

        if (name := args['name']) is not None:
            if not match(self._regex['name'], name.strip()):
                errors['name'] = f"Did not match {self._regex['name']}"

            retailer.name = name

        if (address := args['address']) is not None:
            if not match(self._regex['address'], address.strip()):
                errors['address'] = f"Did not match {self._regex['address']}"

            retailer.address = address

        if (phone := args['phone']) is not None:
            if not match(self._regex['phone'], phone.strip()):
                errors['phone'] = f"Did not match {self._regex['phone']}"

            retailer.phone = phone

        if errors:
            abort(400, **errors)

        db.session.commit()

        return retailer

    # - - - DELETE - - -
    @auth.login_required
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(200, 'Done.')
    def delete(self):
        '''DELETE retailer'''
        pid = g.admin.retailer_pid
        retailer = RetailerModel.query.filter_by(pid=pid).first()

        db.session.delete(retailer)
        db.session.commit()

        return {'message': f'deleted "retailer" (pid = {pid})'}
