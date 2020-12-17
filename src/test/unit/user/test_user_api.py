import json

import pytest
from flask import url_for
from werkzeug import Response

from rna.modules.users.model import User


class TestUserAPI(object):

    @pytest.fixture(autouse=True)
    def _client(self, application):
        self.client = application.test_client()

    def test_user_api_get_id(self, admin_user: User):
        resp: Response = self.client.get(url_for('api.users', user_id=admin_user.id))
        assert resp.status_code == 200, "Expecting a user"
        data = json.loads(resp.get_data())
        assert data['username'] == admin_user.username

    def test_user_api_get_not_found(self, admin_user: User):
        resp: Response = self.client.get(url_for('api.users', user_id=151818184))
        assert resp.status_code == 404, f"Not expecting to find anything;response code {resp.status_code}"

    def test_user_api_get_list(self, admin_user: User):
        resp: Response = self.client.get(url_for('api.users'))
        assert resp.status_code == 200, "Expecting a user"
        data = json.loads(resp.get_data())
        assert len(data) == 1
        assert data[0]['username'] == admin_user.username

    def test_user_delete(self, admin_user: User):
        resp: Response = self.client.get(url_for('api.users', user_id=admin_user.id))
        self.assertStatus(resp, 200, "expecting to find a user")
        data = json.loads(resp.get_data())
        assert data['username'] == admin_user.username
        resp2: Response = self.client.delete(url_for('api.users', user_id=admin_user.id))
        self.assertStatus(resp2, 204, "Should have been deleted")
        resp21: Response = self.client.delete(url_for('api.users', user_id=admin_user.id))
        self.assertStatus(resp21, 404, "Should not exist")

        resp3: Response = self.client.get(url_for('api.users', user_id=admin_user.id))
        self.assertStatus(resp3, 404, "expecting to not find a user")

    def assertStatus(self, resp, param, param1):
        assert resp.status_code == param, param1
