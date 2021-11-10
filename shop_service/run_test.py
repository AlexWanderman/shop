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


class Test_0:
    def test_0(self, client, session):
        assert True
