import json
import unittest

from flask import url_for
from werkzeug import Response

from modules.users.model import User
from extensions import db
from test.base import BaseTestCase


def add_admin():
    user = User(username="admin", email="admin@example.com")
    db.session.add(user)
    db.session.commit()
    assert user.id > 0, "needs to be greater than 0"
    user.set_password("password")
    db.session.commit()
    return user


class TestUser(BaseTestCase):

    def test_set_password(self):
        user = add_admin()
        assert user.password_hash != "password", "is plain text"

    def test_check_password(self):
        user = add_admin()
        assert user.check_password("password")

    def test_user_api_get_id(self):
        user = add_admin()
        resp: Response = self.client.get(url_for('api.users', user_id=user.id))
        assert resp.status_code == 200, "Expecting a user"
        data = json.loads(resp.get_data())
        assert data['username'] == user.username

    def test_user_api_get_not_found(self):
        user = add_admin()
        resp: Response = self.client.get(url_for('api.users', user_id=2))
        assert resp.status_code == 404, f"Not expecting to find anything;response code {resp.status_code}"

    def test_user_api_get_list(self):
        user = add_admin()
        resp: Response = self.client.get(url_for('api.users'))
        assert resp.status_code == 200, "Expecting a user"
        data = json.loads(resp.get_data())
        assert len(data) == 1
        assert data[0]['username'] == user.username

    def test_user_delete(self):
        user = add_admin()
        resp: Response = self.client.get(url_for('api.users', user_id=user.id))
        self.assert200(resp, "expecting to find a user")
        data = json.loads(resp.get_data())
        self.assertEqual(data['username'], user.username)
        resp2: Response = self.client.delete(url_for('api.users', user_id=user.id))
        self.assertStatus(resp2, 204, "Should have been deleted")
        resp21: Response = self.client.delete(url_for('api.users', user_id=user.id))
        self.assert404(resp21, "Should not exist")

        resp3: Response = self.client.get(url_for('api.users', user_id=user.id))
        self.assert404(resp3, "expecting to not find a user")


if __name__ == '__main__':
    unittest.main()
