import pytest

from app import create_app, models, db as _db


@pytest.fixture(scope='session')
def app(request):
    return create_app('config.TestingConfig')


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


class SharedData:
    retailers = [
        {
            'name': 'retailer_one',
            'full_name': 'Retailer One',
            'address': 'str. One, 111',
            'phone': '111-111-11',
        },
        {
            'name': 'retailer_two',
            'full_name': 'Retailer Two',
            'address': 'str. Two, 222',
            'phone': '222-222-22',
        }
    ]

    admins = [
        {
            'retailer_id': 1,
            'login': 'admin_1',
            'password': 'Pa$$_W0rd',
            'email': 'admin_1@mail.com',
        },
        {
            'retailer_id': 2,
            'login': 'admin_2',
            'password': 'Pa$$_W0rd',
            'email': 'admin_2@mail.com',
        },
    ]

    patch = {
        'name': 'new_name',
        'full_name': 'New Name',
        'address': 'str. New, 123',
        'phone': '123-123-45',
    }


class Test_0:
    def test_0(self, client, session):
        assert True


class Test_1_Retailers(SharedData):
    ''' Potential client needs to see all retailers on the platform in order to
        buy something. Everyone can get list of retailers. Admins of retailers
        can edit their shops.

        RetailerModel <-- AdminModel
    '''
    def test_0_create(self, client, session):
        '''Create retailers and admins'''
        session.add(models.RetailerModel(**self.retailers[0]))
        session.add(models.RetailerModel(**self.retailers[1]))
        session.add(models.AdminModel(**self.admins[0]))
        session.add(models.AdminModel(**self.admins[1]))
        session.commit()

    def test_1_get(self, client, session):
        '''(GET) Get all retailers'''
        r = client.get('/retailers')
        d = r.json

        assert r.status_code == 200

        for n in range(len(self.retailers)):
            assert 'id' in d[n]
            assert 'name' in d[n] and d[n]['name'] == self.retailers[n]['name']
            assert 'full_name' in d[n] and d[n]['full_name'] == self.retailers[n]['full_name']
            assert 'address' in d[n] and d[n]['address'] == self.retailers[n]['address']
            assert 'phone' in d[n] and d[n]['phone'] == self.retailers[n]['phone']
            assert 'datetime_join' in d[n]

    def test_2_patch(self, client, session):
        '''(PATCH) Change retailer'''
        r = client.patch(
            '/retailers',
            json=self.patch,
            auth=(
                self.admins[0]['login'],
                self.admins[0]['password'],
            )
        )
        d = r.json

        assert r.status_code == 200

        assert 'id' in d and d['id'] == 1
        assert 'name' in d and d['name'] == self.patch['name']
        assert 'full_name' in d and d['full_name'] == self.patch['full_name']
        assert 'address' in d and d['address'] == self.patch['address']
        assert 'phone' in d and d['phone'] == self.patch['phone']
        assert 'datetime_join' in d

    @pytest.mark.parametrize('name, value', (
        ('name', 'sh#p_привет'),
        ('name', 'TooLongName_999_999_999_999_999_999'),
        ('full_name', 'Sh#p!'),
        ('full_name', 'TooLongName_999_999_999_999_999_999'),
        ('address', f'str. Long, {"6" * 666}'),
        ('phone', '1-123-12345'),
    ))
    def test_3_patch_invalid(self, client, session, name, value):
        '''(PATCH) Test validation'''
        r = client.patch(
            '/retailers',
            json={**self.patch, name: value},
            auth=(
                self.admins[0]['login'],
                self.admins[0]['password'],
            )
        )
        d = r.json

        assert r.status_code == 400


class Test_2_Sections(SharedData):
    ''' Every shop must have some sections whitch will hold products. For
        example: "Summer sail", "Dairy", "Pizza". Everyone can see the list of
        available (sections can be disabled) sections. Admins can see all
        sections of their retailer (admins are bound to retailers) and manage
        them (create, update, delete if empty).

        RetailerModel <-- SectionModel
    '''
    @pytest.mark.parametrize('admin, name, is_active', (
        (0, 'R1 S1 Active', '1'),
        (0, 'R1 S2 Active', '1'),
        (0, 'R1 S3 Inactive', ''),
        (1, 'R2 S1 Active', '1'),
        (1, 'R2 S2 Active', '1'),
        (1, 'R2 S3 Inactive', ''),
    ))
    def test_0_post(self, client, session, admin, name, is_active):
        '''(POST) Create section for retailer'''
        r = client.post(
            '/section',
            json={'name': name, 'is_active': is_active},
            auth=(
                self.admins[admin]['login'],
                self.admins[admin]['password'],
            )
        )
        d = r.json

        assert r.status_code == 201

    @pytest.mark.parametrize('admin, retailer_id', ((0, 1), (0, 2), (1, 1), (1, 2)))
    def test_1_get_admin_access(self, client, session, admin, retailer_id):
        '''(GET) Read sections of retailer'''
        r = client.get(
            f'/sections/{retailer_id}',
            auth=(
                self.admins[admin]['login'],
                self.admins[admin]['password'],
            )
        )
        d = r.json

        assert r.status_code == 200

    @pytest.mark.parametrize('retailer_id', (1, 2))
    def test_1_get_normal_access(self, client, session, retailer_id):
        '''(GET) Read sections of retailer'''
        r = client.get(f'/sections/{retailer_id}')
        d = r.json

        assert r.status_code == 200

    # def test_2_patch(self, client, session):
    #     '''(PATCH) Update section of retailer'''
    #     assert False

    # def test_3_delete(self, client, session):
    #     '''(DELETE) Delete section of retailer'''
    #     assert False


class Test_3_Products:
    ''' Every section of a retailer can have products. For example: "Winter
        boots", "Milk chocolate", "Brand Printer 3000". Everyone can see the
        list of products available (they can be disabled). Admins can see full
        list of producst, create new and change existing. Products can not be
        deleted, but can be disabled. In disabled sections all products count
        as disabled.

        RetailerModel <-- SectionModel <-- ProductModel
    '''
    def test_0_post(self, client, session):
        '''(POST) Create product for retailer'''
        assert False

    def test_1_get(self, client, session):
        '''(GET) Read products of retailer'''
        assert False

    def test_2_patch(self, client, session):
        '''(PATCH) Update product of retailer'''
        assert False
