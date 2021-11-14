import pytest

from app import create_app, models, db as _db


@pytest.fixture(scope='session')
def app(request):
    app = create_app()
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
    def test_0(self, client, session):
        assert True
    
    @pytest.mark.parametrize('login, email, password, first_name, last_name', (
        ('user_1', 'user_1@mail.com', 'Fname', 'Lname'),
        ('user_2', 'user_2@mail.com', 'Fname', 'Lname'),
        ('user_3', 'user_3@mail.com', 'Fname', 'Lname'),
    ))
    def test_1(self, client, session, login, email, password, first_name, last_name):
        session.add(models.UserModel(login, email, password, first_name, last_name))
        session.commit()
