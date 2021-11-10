from re import match

from flask import g
from flask_restx import Resource, abort, fields

from app import api, auth, db
from app.models import RetailerModel, SectionModel


# Namespace
ns = api.namespace(
    'Sections',
    description='Everyone can get list of all active sections. Sections can be '
                'inactive (is_active = False), in that case only admins of their '
                'retailers can see them. Same with editing and deleting.',
    path='/',
)


# Input
_ = post_section = ns.parser()
_.add_argument('name', type=str, required=True, help='Sections name')
_.add_argument('about', type=str, required=True, help='Some info about section')
_.add_argument('is_active', type=bool, required=True, help='Can it be accessed by all')

_ = patch_section = ns.parser()
_.add_argument('pid', type=str, required=False, help='Personal IDentifier')
_.add_argument('name', type=str, required=False, help='Sections name')
_.add_argument('about', type=str, required=False, help='Some info about section')
_.add_argument('is_active', type=bool, required=False, help='Can it be accessed by all')


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
class SectionRead(Resource):
    # - - - GET - - -
    @auth.login_required(optional=True)
    @ns.response(404, 'Retailer not found.')
    @ns.marshal_with(section_model, True, 200, 'List of sections.')
    def get(self, retailer_pid):
        '''GET list of all sections'''

        if not RetailerModel.query.filter_by(pid=retailer_pid).first():
            abort(404, message='Retailer not found.')

        # If this is admin and belongs the same retailer
        if auth.current_user() and g.admin.retailer_pid == retailer_pid:
            return SectionModel.query.filter_by(retailer_pid=retailer_pid).all()

        # If not admin or from other retailer
        return SectionModel.query.filter_by(retailer_pid=retailer_pid, is_active=True).all()


@ns.route('/section/<section_pid>')
class SectionChange(Resource):
    _regex = {
        'pid': r'^[a-zA-Z0-9_]{3,32}$',
        'name': r'^[\w\d ]{3,32}$',
        'about': r'.{3,64}',
    }

    # - - - POST - - -
    @auth.login_required
    @ns.expect(post_section)
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(400, 'Invalid input data.')
    @ns.response(404, 'Section not found.')
    @ns.marshal_with(section_model, False, 201, 'Created section.')
    def post(self, section_pid):
        '''POST new section'''
        args = post_section.parse_args()

        errors = {}

        if not match(self._regex['pid'], (pid := section_pid)):
            errors['pid'] = f"Did not match {self._regex['pid']}"

        # No need to input what you already know
        retailer_pid = g.admin.retailer_pid

        if not match(self._regex['name'], (name := args['name'].strip())):
            errors['name'] = f"Did not match {self._regex['name']}"

        if not match(self._regex['about'], (about := args['about'].strip())):
            errors['about'] = f"Did not match {self._regex['about']}"

        # Have not found how to brake it
        is_active = args['is_active']

        if errors:
            abort(400, **errors)

        section = SectionModel(
            pid=pid,
            retailer_pid=retailer_pid,
            name=name,
            about=about,
            is_active=is_active,
        )

        db.session.add(section)
        db.session.commit()

        return section

    # - - - PATCH - - -
    @auth.login_required
    @ns.expect(patch_section)
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(403, 'Admin-Retailer mistmatch.')
    @ns.response(400, 'Invalid input data.')
    @ns.response(404, 'Section not found.')
    @ns.marshal_with(section_model, False, 200, 'Edited section.')
    def patch(self, section_pid):
        '''PATCH section'''
        args = patch_section.parse_args()

        section = SectionModel.query.filter_by(pid=section_pid).first()
        if not section:
            abort(404, 'Section not found.')

        if section.retailer_pid != g.admin.retailer_pid:
            abort(403, 'Admin-Retailer mistmatch.')

        errors = {}

        if (pid := args['pid']) is not None:
            if not match(self._regex['pid'], pid.strip()):
                errors['pid'] = f"Did not match {self._regex['pid']}"

            section.pid = pid

        if (name := args['name']) is not None:
            if not match(self._regex['name'], name.strip()):
                errors['name'] = f"Did not match {self._regex['name']}"

            section.name = name

        if (about := args['about']) is not None:
            if not match(self._regex['about'], about.strip()):
                errors['about'] = f"Did not match {self._regex['about']}"

            section.about = about

        if (is_active := args['is_active']) is not None:
            section.is_active = is_active

        db.session.commit()

        return section

    # - - - DELETE - - -
    @auth.login_required
    @ns.response(401, 'Auth was not provided or wrong.')
    @ns.response(403, 'Admin-Retailer mistmatch.')
    @ns.response(404, 'Section not found.')
    @ns.response(200, 'Done.')
    def delete(self, section_pid):
        '''Delete section'''

        section = SectionModel.query.filter_by(pid=section_pid).first()
        if not section:
            abort(404, 'Section not found.')

        if section.retailer_pid != g.admin.retailer_pid:
            abort(403, 'Admin-Retailer mistmatch.')

        db.session.delete(section)
        db.session.commit()

        return {'message': f'deleted "section" (pid = {section_pid})'}
