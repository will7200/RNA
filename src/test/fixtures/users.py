import pytest
from flask import url_for
from flask.testing import FlaskClient

from rna.extensions import db
from rna.modules.users.model import User, Role


@pytest.fixture
def admin_user():
    """Creates a admin user."""
    user = User(username="test_admin", email="test_admin@example.org")
    user.set_password("password")
    user.roles.append(Role(name="admin"))
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def power_user():
    """Creates a another admin user."""
    user = User(username="power_user", email="power_user@example.org")
    user.set_password("password")
    user.roles.append(Role(name="admin"))
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def regular_user():
    """Create a normal user"""
    user = User(username="user", email="user@example.org")
    user.set_password("password")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def invalid_user():
    user = User(username="test_admin1", email="test_admin@example.org", active=False)
    user.set_password("password")
    user.roles.append(Role(name="admin"))
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def authenticated_admin(client, admin_user):
    res = client.post(url_for('app.login'), data=dict(username='test_admin', password='password'),
                      follow_redirects=True)
    assert res.status_code == 200


@pytest.fixture
def authenticated_power_user(application, power_user):
    app = application
    ctx = application.test_request_context()
    ctx.push()
    app.test_client_class = FlaskClient
    client = app.test_client()

    res = client.post(url_for('app.login'), data=dict(username='power_user', password='password'),
                      follow_redirects=True)
    assert res.status_code == 200
    return client
