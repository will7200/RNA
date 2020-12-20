import pytest

from rna.extensions import db
from rna.modules.remote_management.models import Host, HostCommand
from rna.modules.users.model import User


@pytest.fixture
def localhost(admin_user: User):
    """Creates a host """
    host = Host(name="localhost", hostname="localhost", port=22,
                username="root", authentication_method="password",
                password="password", user_id=admin_user.id)
    db.session.add(host)
    db.session.commit()
    return host


@pytest.fixture
def localhost_command():
    """Creates a host """
    host = Host(name="localhost", hostname="localhost", port=22,
                username="root", authentication_method="password",
                password="password")
    host.commands.append(HostCommand(
        command="ip route",
        status=True,
    ))
    db.session.add(host)
    db.session.commit()
    return host
