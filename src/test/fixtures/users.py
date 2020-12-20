import pytest
from flask import url_for

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
