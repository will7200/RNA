import pytest
from flask.testing import FlaskClient

from rna.app import create_app
from rna.extensions import db
from test.unit.base import TestBaseConfig


@pytest.fixture(autouse=True)
def application():
    """application with context."""
    app = create_app(TestBaseConfig())

    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture()
def request_context(application):
    with application.test_request_context():
        yield


@pytest.fixture()
def post_request_context(application):
    with application.test_request_context(method="POST"):
        yield


@pytest.fixture(autouse=True)
def database():
    """database setup."""
    db.create_all()  # Maybe use migration instead?

    yield db

    db.drop_all()


@pytest.fixture()
def client(application):
    app = application
    ctx = application.test_request_context()
    ctx.push()
    app.test_client_class = FlaskClient
    return app.test_client()
