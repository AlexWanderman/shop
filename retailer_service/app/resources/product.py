from re import match

from flask import g
from flask_restx import Resource, abort, fields

from app import api, auth, db
from app.models import RetailerModel, SectionModel, ProductModel


# Namespace
ns = api.namespace(
    'Products',
    description='Everyone can get list of all active products. Products can be '
                'inactive (is_active = False or if their section is inaction), '
                'in that case only admins of their retailers can see them. '
                'Same with editing and deleting.',
    path='/',
)


# Input
_ = post_product = ns.parser()
_.add_argument('section_pid', type=str, required=True, help='Sections pid')
_.add_argument('name', type=str, required=True, help='Products name')
_.add_argument('about', type=str, required=True, help='Some info about product')
_.add_argument('price', type=int, required=True, help='Products price')
_.add_argument('is_active', type=bool, required=True, help='Can it be accessed by all')

_ = patch_product = ns.parser()
_.add_argument('pid', type=str, required=False, help='Personal IDentifier')
_.add_argument('name', type=str, required=False, help='Products name')
_.add_argument('about', type=str, required=False, help='Some info about product')
_.add_argument('price', type=int, required=False, help='Products price')
_.add_argument('is_active', type=bool, required=False, help='Can it be accessed by all')


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
    'is_active': fields.Boolean(
        description='Can it be accessed by all',
        example=True,
    ),
})


@ns.route('/products/<section_pid>')
class ProductRead(Resource):
    # - - - GET - - -
    @auth.login_required(optional=True)
    @ns.response(404, 'Section not found.')
    @ns.marshal_with(product_model, True, 200, 'List of products.')
    def get(self, section_pid):
        '''GET list of all products'''

        section = SectionModel.query.filter_by(pid=section_pid).first()
        if not section:
            abort(404, message='Section not found.')

        # If this is admin and belongs the same retailer
        if auth.current_user() and g.admin.retailer_pid == section.retailer_pid:
            return section.products.all()

        # If not admin or from other retailer
        if not section.is_active:
            abort(404, 'Section not found.')

        return section.products.filter_by(is_active=True).all()


@ns.route('/product/<product_pid>')
class ProductChange(Resource):
    _regex = {
        'pid': r'^[a-zA-Z0-9_]{3,32}$',
        'name': r'^[\w\d ]{3,32}$',
        'about': r'.{3,64}',
    }

    # - - - POST - - -
    @auth.login_required
    @ns.expect(post_product)
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(403, 'Admin-Retailer mistmatch.')
    @ns.response(400, 'Invalid input data.')
    @ns.response(404, 'Product not found.')
    @ns.marshal_with(product_model, False, 201, 'Created product.')
    def post(self, product_pid):
        '''POST new product'''
        args = post_product.parse_args()

        # TODO Check if admin retailer == product retailer

        errors = {}

        if not match(self._regex['pid'], (pid := product_pid)):
            errors['pid'] = f"Did not match {self._regex['pid']}"

        if not match(self._regex['pid'], (section_pid := args['section_pid'].strip())):
            errors['section_pid'] = f"Did not match {self._regex['pid']}"

        section = SectionModel.query.filter_by(pid=section_pid).first()
        if section.retailer_pid != g.admin.retailer_pid:
            abort(403, 'Admin-Retailer mistmatch.')

        if not match(self._regex['name'], (name := args['name'].strip())):
            errors['name'] = f"Did not match {self._regex['name']}"

        if not match(self._regex['about'], (about := args['about'].strip())):
            errors['about'] = f"Did not match {self._regex['about']}"

        if not (0 < (price := args['price']) < 1_000_000):
            errors['price'] = f'Invalid price ({price} is not in range 0 < n < 1 000 000)'

        # Have not found how to brake it
        is_active = args['is_active']

        if errors:
            abort(400, **errors)

        product = ProductModel(
            pid=pid,
            section_pid=section_pid,
            name=name,
            about=about,
            price=price,
            is_active=is_active,
        )

        db.session.add(product)
        db.session.commit()

        return product

    # - - - PATCH - - -
    @auth.login_required
    @ns.expect(patch_product)
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(403, 'Admin-Retailer mistmatch.')
    @ns.response(400, 'Invalid input data.')
    @ns.response(404, 'Product not found.')
    @ns.marshal_with(product_model, False, 200, 'Edited product.')
    def patch(self, product_pid):
        '''PATCH product'''
        args = patch_product.parse_args()

        product = ProductModel.query.filter_by(pid=product_pid).first()
        if not product:
            abort(404, 'Product not found.')

        section = SectionModel.query.filter_by(pid=product.section_pid).first()
        if section.retailer_pid != g.admin.retailer_pid:
            abort(403, 'Admin-Retailer mistmatch.')

        errors = {}

        if (pid := args['pid']) is not None:
            if not match(self._regex['pid'], pid.strip()):
                errors['pid'] = f"Did not match {self._regex['pid']}"

            product.pid = pid

        if (name := args['name']) is not None:
            if not match(self._regex['name'], name.strip()):
                errors['name'] = f"Did not match {self._regex['name']}"

            product.name = name

        if (about := args['about']) is not None:
            if not match(self._regex['about'], about.strip()):
                errors['about'] = f"Did not match {self._regex['about']}"

            product.about = about

        if (price := args['price']) is not None:
            if not (0 < (price := args['price']) < 1_000_000):
                errors['price'] = f'Invalid price ({price} is not in range 0 < n < 1 000 000)'

            product.price = price

        if (is_active := args['is_active']) is not None:
            product.is_active = is_active

        db.session.commit()

        return product

    # - - - DELETE - - -
    @auth.login_required
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(403, 'Admin-Retailer mistmatch.')
    @ns.response(404, 'Product not found.')
    @ns.response(200, 'Done.')
    def delete(self, product_pid):
        '''Delete product'''

        product = ProductModel.query.filter_by(pid=product_pid).first()
        if not product:
            abort(404, 'Product not found.')

        section = SectionModel.query.filter_by(pid=product.section_pid).first()
        if section.retailer_pid != g.admin.retailer_pid:
            abort(403, 'Admin-Retailer mistmatch.')

        db.session.delete(product)
        db.session.commit()

        return {'message': f'deleted "product" (pid = {product_pid})'}
