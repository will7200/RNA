import pytest

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


@pytest.fixture()
def invalid_user():
    user = User(username="test_admin1", email="test_admin@example.org", active=False)
    user.set_password("password")
    user.roles.append(Role(name="admin"))
    db.session.add(user)
    db.session.commit()
    return user
