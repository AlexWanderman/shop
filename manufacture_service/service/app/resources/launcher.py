from re import match

from flask import g
from flask_restx import Resource, abort, fields

from app import api, auth, db
from app.models.launcher import LauncherModel


# Namespace
ns = api.namespace(
    'Launcher',
    description='Manage manufacturers list of supplies for each retailer',
    path='/',
)


# Input
_ = post_launcher = ns.parser()
_.add_argument('retailer_pid', type=str, required=True, help='Retailers pid')
_.add_argument('products', type=dict[str, int], required=True, help='Retailers pid')
# products -> {product_pid: (amount, is_active), ...}

_ = patch_launcher = ns.parser()
_.add_argument('amount', type=int, required=False, help='How much products to send')
_.add_argument('is_active', type=bool, required=False, help='Inactive will not be send')


# Output
launcher_model = ns.model('LauncherModel', {
    'aid': fields.String(
        description='Automatic IDentifier',
        example='ATN95dAXHmkjQdFQmYRhKnP0zt23YpDT',
    ),
    'manufacture_pid': fields.String(
        description='Manufactures pid',
        example='super_retailer',
    ),
    'retailer_pid': fields.String(
        description='Admins login',
        example='super_shop',
    ),
    'product_pid': fields.String(
        description='Admins login',
        example='hott_pizza',
    ),
    'amount': fields.Integer(
        description='Admins login',
        example=30,
    ),
    'is_active': fields.Boolean(
        description='Admins login',
        example=True,
    ),
})


@ns.route('/launchers')
class Launchers(Resource):
    _regex = {
        'pid': r'^[a-zA-Z0-9_]{3,32}$',
    }

    @auth.login_required
    @ns.response(401, 'Invalid or missing auth.')
    @ns.marshal_with(launcher_model, True, 201, 'List of all launchers.')
    def get(self):
        '''GET list of all launchers (who, what and how much to supply)'''
        return LauncherModel.query.filter_by(
            manufacture_pid=g.admin.manufacture_pid,
        ).order_by(
            LauncherModel.manufacture_pid,
        ).all()

    @auth.login_required
    @ns.expect(post_launcher)
    @ns.response(401, 'Invalid or missing auth.')
    @ns.response(400, 'Invalid input.')
    @ns.marshal_with(launcher_model, True, 201, 'Created.')
    def post(self):
        '''POST list of launchers (who, list of what and how much for each)'''
        args = post_launcher.parse_args()
        manufacture_pid = g.admin.manufacture_pid

        if not (retailer_pid := args['retailer_pid']):
            abort(400, 'Retailer PID missing.')

        if not (products := args['products']):
            abort(400, 'Product list can not be emty.')

        if len(products) > 999:
            abort(400, 'Product list can not contain more then 999 items.')

        launhcers = []
        errors = {}

        if not match(self._regex['pid'], retailer_pid):
            errors[retailer_pid] = f"Did not match {self._regex['pid']}"

        for product_pid, params in products.items():
            amount = params[0]
            is_active = params[1]

            product_pid = product_pid.strip()

            if not match(self._regex['pid'], product_pid):
                errors[product_pid] = f"Did not match {self._regex['pid']}"

            if not (0 < amount < 10_000):
                errors[product_pid] = f"Amount {amount} not in range 0 < amount < 10000."

            launcher = LauncherModel(
                manufacture_pid=manufacture_pid,
                retailer_pid=retailer_pid,
                product_pid=product_pid,
                amount=amount,
                is_active=is_active,
            )
            launhcers.append(launcher)
            db.session.add(launcher)

        if errors:
            abort(400, **errors)

        db.session.commit()

        return launhcers


@ns.route('/launcher/<laucher_aid>')
class LauncherEdit(Resource):
    @auth.login_required
    @ns.expect(patch_launcher)
    @ns.response(401, 'Invalid or missing auth.')
    @ns.response(403, 'Admin-Launcher manufacture mistmatch.')
    @ns.response(404, 'Launcher not found.')
    @ns.response(400, 'Invalid input.')
    @ns.marshal_with(launcher_model, False, 200, 'Updated.')
    def patch(self, laucher_aid):
        args = patch_launcher.parse_args()

        if not (launcher := LauncherModel.query.filter_by(aid=laucher_aid).first()):
            abort(404, 'Launcher not found.')

        if launcher.manufacture_pid != g.admin.manufacture_pid:
            abort(403, 'Retailer-Launcher manufacture mistmatch.')

        errors = {}

        if (amount := args['amount']) is not None:
            if not (0 < amount < 10_000):
                errors['amount'] = f"Amount {amount} not in range 0 < amount < 10000."

            launcher.amount = amount

        if (is_active := args['is_active']) is not None:
            launcher.is_active = is_active

        if errors:
            abort(400, **errors)

        db.session.commit()

        return launcher

    @auth.login_required
    @ns.response(401, 'Invalid or missing auth.')
    @ns.response(403, 'Admin-Launcher manufacture mistmatch.')
    @ns.response(404, 'Launcher not found.')
    @ns.response(200, 'Done.')
    def delete(self, laucher_aid):
        if not (launcher := LauncherModel.query.filter_by(aid=laucher_aid).first()):
            abort(404, 'Launcher not found.')

        if launcher.manufacture_pid != g.admin.manufacture_pid:
            abort(403, 'Admin-Launcher manufacture mistmatch.')

        retailer = launcher.retailer_pid
        product = launcher.product_pid
        amount = launcher.amount

        db.session.delete(launcher)
        db.session.commit()

        return {'message': f'Deleted: {retailer = } {product = } {amount = }'}
