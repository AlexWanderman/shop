''' Tests depends on each other, so can only be deployed all at once.
'''
import pytest

from app import create_app, models, db as _db


@pytest.fixture(scope='session')
def app(request):
    app = create_app()
    app.testing = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


@pytest.fixture(autouse=True)
def _setup_app_context_for_test(request, app):
    ctx = app.app_context()
    ctx.push()
    yield
    ctx.pop()


@pytest.fixture(scope='session')
def db(request, app):
    with app.app_context():
        _db.create_all()
        yield _db
        # _db.drop_all()


@pytest.fixture(scope='function')
def session(request, app, db):
    connection = _db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = _db.create_scoped_session(options=options)

    _db.session = session

    yield session

    # transaction.rollback()
    # connection.close()
    # session.remove()


class Test_0:
    '''Just to make shure that pytest works.'''
    def test_0(self, client, session):
        assert True


class Test_1_Retailers:
    @pytest.mark.parametrize('pid, name, address, phone', (
        ('shop_1', 'Shop 1', 'str. One, 1', '123-123-11'),
        ('shop_2', 'Shop 2', 'str. Two, 1', '123-123-22'),
        ('shop_3', 'Shop 3', 'str. Three, 1', '123-123-33'),
    ))
    def test_1_1_post_positive(self, client, session, pid, name, address, phone):
        data = {
            'pid': pid,
            'name': name,
            'address': address,
            'phone': phone,
        }

        r = client.post('/retailer', json=data)
        assert r.status_code == 200

        d = r.json
        assert d == data

    @pytest.mark.parametrize('pid, name, address, phone', (
        ('магаз', 'Shop 1', 'str. One, 1', '123-123-11'),
        ('shop_2', '!!!', 'str. Two, 1', '123-123-22'),
        ('shop_3', 'Shop 3', '', '123-123-33'),
        ('shop_4', 'Shop 4', 'str. Three, 1', '123-123-444'),
    ))
    def test_1_2_post_negative(self, client, session, pid, name, address, phone):
        data = {
            'pid': pid,
            'name': name,
            'address': address,
            'phone': phone,
        }

        r = client.post('/retailer', json=data)
        assert r.status_code == 400

    def test_1_3_get(self, client, session):
        r = client.get('/retailers')
        assert r.status_code == 200


class Test_2_Admins:
    @pytest.mark.parametrize('pid, retailer_pid, login, password', (
        ('admin_1', 'shop_1', 'admin_1', 'aA#45678'),
        ('admin_2', 'shop_2', 'admin_2', 'aA#45678'),
        ('admin_3', 'shop_3', 'admin_3', 'aA#45678'),
    ))
    def test_2_1_post_positive(self, client, session, pid, retailer_pid, login, password):
        data = {
            'pid': pid,
            'retailer_pid': retailer_pid,
            'login': login,
            'password': password,
        }

        r = client.post('/admin', json=data)
        assert r.status_code == 200

        d = r.json
        d['password'] = password  # It will not be returned
        assert d == data

    @pytest.mark.parametrize('pid, retailer_pid, login, password', (
        ('блабла', 'shop_1', 'admin_1', 'aA#45678'),
        ('admin_2', 'уфуф', 'admin_2', 'aA#45678'),
        ('admin_3', 'shop_3', 'йцуу', 'aA#45678'),
        ('admin_3', 'shop_3', 'admin_3', 'password'),
    ))
    def test_2_2_post_negative(self, client, session, pid, retailer_pid, login, password):
        data = {
            'pid': pid,
            'retailer_pid': retailer_pid,
            'login': login,
            'password': password,
        }

        r = client.post('/admin', json=data)
        assert r.status_code == 400

    @pytest.mark.parametrize('pid, retailer_pid, login, password', (
        ('admin_1', 'shop_1', 'admin_1', 'aA#45678'),
        ('admin_2', 'shop_2', 'admin_2', 'aA#45678'),
        ('admin_3', 'shop_3', 'admin_3', 'aA#45678'),
    ))
    def test_2_3_get(self, client, session, pid, retailer_pid, login, password):
        r = client.get('/admin', auth=(login, password))
        assert r.status_code == 200

        d = r.json
        data = {
            'pid': pid,
            'retailer_pid': retailer_pid,
            'login': login,
        }
        assert d == data


class Test_3_Sections:
    @pytest.mark.parametrize('login, password, pid, retailer_pid, name, about, is_active', (
        ('admin_1', 'aA#45678', 'section_1_1', 'shop_1', 'Section 1', 'About 1', True),
        ('admin_1', 'aA#45678', 'section_1_2', 'shop_1', 'Section 2', 'About 2', False),

        ('admin_2', 'aA#45678', 'section_2_1', 'shop_2', 'Section 1', 'About 1', True),
        ('admin_2', 'aA#45678', 'section_2_2', 'shop_2', 'Section 2', 'About 2', False),

        ('admin_3', 'aA#45678', 'section_3_1', 'shop_3', 'Section 1', 'About 1', True),
        ('admin_3', 'aA#45678', 'section_3_2', 'shop_3', 'Section 2', 'About 2', False),
    ))
    def test_3_1_post_positive(self, client, session, login, password, pid, retailer_pid, name, about, is_active):
        data = {
            'name': name,
            'about': about,
            'is_active': is_active,
        }

        r = client.post(f'/section/{pid}', json=data, auth=(login, password))
        assert r.status_code == 200

        d = r.json
        data['pid'] = pid
        data['retailer_pid'] = retailer_pid  # It should not be send
        assert d == data

    @pytest.mark.parametrize('login, password, pid, name, about', (
        ('admin_1', 'aA#45678', 'бред', 'Section 1', 'About 1'),
        ('admin_1', 'aA#45678', 'section_1_1', 'б', 'About 1'),
        ('admin_1', 'aA#45678', 'section_1_1', 'Section 1', 'б'),
    ))
    def test_3_2_post_negative(self, client, session, login, password, pid, name, about):
        data = {
            'name': name,
            'about': about,
            'is_active': True,
        }

        r = client.post(f'/section/{pid}', json=data, auth=(login, password))
        assert r.status_code == 400

    @pytest.mark.parametrize('login, password, pid, retailer_pid, name, about, is_active', (
        ('admin_1', 'aA#45678', 'section_1_1', 'shop_1', 'Section 1', 'About 1', True),
        ('admin_1', 'aA#45678', 'section_1_2', 'shop_1', 'Section 2', 'About 2', False),

        ('admin_2', 'aA#45678', 'section_2_1', 'shop_2', 'Section 1', 'About 1', True),
        ('admin_2', 'aA#45678', 'section_2_2', 'shop_2', 'Section 2', 'About 2', False),

        ('admin_3', 'aA#45678', 'section_3_1', 'shop_3', 'Section 1', 'About 1', True),
        ('admin_3', 'aA#45678', 'section_3_2', 'shop_3', 'Section 2', 'About 2', False),
    ))
    def test_3_3_get(self, client, session, login, password, pid, retailer_pid, name, about, is_active):
        if login:
            r = client.get('/admin', auth=(login, password))
        else:
            r = client.get('/admin')

        # TODO ---

        assert r.status_code == 200

        d = r.json
        data = {
            'pid': pid,
            'retailer_pid': retailer_pid,
            'name': name,
            'about': about,
            'is_active': is_active,
        }
        assert d == data
