from datetime import datetime
from re import match

from flask import g
from flask_restx import Resource, abort, fields

from app import api, auth, db
from app.models import RetailerModel, ContractModel, ProductModel, TransactionModel


# Namespace
ns = api.namespace(
    'Retail',
    description='Buy and import products.',
    path='/',
)


# Input
_ = post_import = ns.parser()
_.add_argument('retailer_pid', type=str, required=True, help='Retailers pid')
_.add_argument('products', type=dict[str, int], required=True, help='Retailers pid')
# products -> {product_pid: amount, ...}

_ = post_buy = ns.parser()
_.add_argument('retailer_pid', type=str, required=True, help='Retailers pid')
_.add_argument('products', type=dict[str, int], required=True, help='Retailers pid')
# products -> {product_pid: amount, ...}
_.add_argument('pay_method', type=str, required=True, help='Pay method')


# Output
class TransactionField(fields.Raw):
    def format(self, value):
        return {
            'product_pid': value.product_pid,
            'amount': value.amount,
            'sold_at': value.sold_at,
        }


contract_model = ns.model('ContractModel', {
    'aid': fields.String(
        description='Automatic IDentifier',
        example='summer_sail',
    ),
    'retailer_pid': fields.String(
        description='Retailers pid',
        example='hott_pizza',
    ),
    'pay_method': fields.String(
        description='Pay method',
        example=ContractModel.get_pay_methods(),
    ),
    'datetime': fields.DateTime(
        description='Date and time of contract.',
        example=str(datetime.utcnow()),
    ),
    'transactions': fields.List(TransactionField),
})


@ns.route('/contract/<contract_aid>')
class Contract(Resource):
    # - - - GET - - -
    @ns.response(404, 'Contract not found.')
    @ns.marshal_with(contract_model, False, 200, 'Contract and transactions.')
    def get(self, contract_aid):
        '''GET contract info and its transactions'''
        contract = ContractModel.query.filter_by(aid=contract_aid).first()
        if not contract:
            abort(404, 'Contract not found.')

        transactions = TransactionModel.query.filter_by(contract_aid=contract_aid).all()
        if not transactions:
            abort(404, 'Transactions was not found.')

        return contract


@ns.route('/import')
class Import(Resource):
    # - - - POST - - -
    @ns.expect(post_import)
    @ns.response(400, 'Invalid input data.')
    @ns.response(404, 'Retailer/Product not found.')
    @ns.response(200, 'Import request successful.')
    def post(self):
        '''Import products TO retailer'''
        args = post_import.parse_args()

        retailer_pid = args['retailer_pid']
        if not RetailerModel.query.filter_by(pid=retailer_pid).first():
            abort(404, 'Retailer not found.')

        products = args['products']
        if not products:
            abort(400, 'Product list can not be emty.')

        if len(products) > 999:
            abort(400, 'Product list can not contain more then 999 items.')

        contract = ContractModel(
            retailer_pid=retailer_pid,
            pay_method=None,
        )
        transactions = []
        errors = {}

        for product_pid, amount in products.items():
            product = ProductModel.query.filter_by(pid=product_pid).first()
            if not product:
                errors[f'{product_pid}'] = 'Product not found.'
                continue

            if product.section.retailer_pid != retailer_pid:
                errors[f'{product_pid}'] = 'Product belongs to another retailer.'
                continue

            # Import even inactive products
            # if not product.section.is_active or not product.is_active:
            #     errors[f'{product_pid}'] = 'Product is unavailable.'
                continue

            if not (0 < amount < 1000):
                errors[f'{product_pid}'] = f'Amount must be in range 0 < amount < 1000, got {amount}.'
                continue

            transactions.append(TransactionModel(
                contract_aid=contract.aid,
                product_pid=product.pid,
                sold_at=0,
                amount=amount,
            ))

        if errors:
            abort(400, **errors)

        db.session.add(contract)
        db.session.add_all(transactions)
        db.session.commit()

        return {'contract_aid': contract.aid}


@ns.route('/buy')
class Buy(Resource):
    # - - - POST - - -
    @ns.expect(post_buy)
    @ns.response(400, 'Invalid input data.')
    @ns.response(404, 'Retailer/Section/Product not found.')
    @ns.response(200, 'Buy request successful.')
    def post(self):
        '''Buy products FROM retailer'''
        args = post_buy.parse_args()

        retailer_pid = args['retailer_pid']
        if not RetailerModel.query.filter_by(pid=retailer_pid).first():
            abort(404, 'Retailer not found.')

        products = args['products']
        if not products:
            abort(400, 'Product list can not be emty.')

        pay_method = args['pay_method']
        if pay_method not in ContractModel.get_pay_methods():
            abort(400, f'Pay method must be one of {ContractModel.get_pay_methods()}')

        if len(products) > 999:
            abort(400, 'Product list can not contain more then 999 items.')

        contract = ContractModel(
            retailer_pid=retailer_pid,
            pay_method=pay_method,
        )

        transactions = []
        errors = {}

        for product_pid, amount in products.items():
            product = ProductModel.query.filter_by(pid=product_pid).first()
            if not product:
                errors[f'{product_pid}'] = 'Product not found.'
                continue

            if product.section.retailer_pid != retailer_pid:
                errors[f'{product_pid}'] = 'Product belongs to another retailer.'
                continue

            if not product.section.is_active or not product.is_active:
                errors[f'{product_pid}'] = 'Product is unavailable.'
                continue

            if not (0 < amount < 100):
                errors[f'{product_pid}'] = f'Amount must be in range 0 < amount < 100, got {amount}.'
                continue

            if amount > product.in_stock:
                errors[f'{product_pid}'] = f'Demand is too high (got {product.in_stock}, asked for {amount}).'
                continue

            transactions.append(TransactionModel(
                contract_aid=contract.aid,
                product_pid=product.pid,
                sold_at=product.price,
                amount=(amount * -1),
            ))

        if errors:
            abort(400, **errors)

        db.session.add(contract)
        db.session.add_all(transactions)
        db.session.commit()

        return {'contract_aid': contract.aid}
