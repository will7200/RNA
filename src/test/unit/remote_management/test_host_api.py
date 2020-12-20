import json

import pytest
from flask import url_for
from werkzeug import Response

from rna.modules.remote_management.models import Host


@pytest.mark.usefixtures('authenticated_admin')
class TestHostAPI(object):

    def test_get_host(self, localhost: Host, client):
        resp: Response = client.get(url_for('api.hosts', host_id=localhost.id))
        assert resp.status_code == 200, "Expecting a host"
        data = json.loads(resp.get_data())
        assert data['name'] == localhost.name

    def test_get_host_not_found(self, client):
        resp: Response = client.get(url_for('api.hosts', host_id=151818184))
        assert resp.status_code == 404, f"Not expecting to find anything;response code {resp.status_code}"

    def test_host_list(self, client, localhost: Host):
        resp: Response = client.get(url_for('api.hosts'))
        assert resp.status_code == 200, "Expecting a 200 response"
        data = json.loads(resp.get_data())
        assert len(data) == 1
        assert data[0]['name'] == localhost.name

    def test_host_delete(self, client, localhost: Host):
        resp: Response = client.get(url_for('api.hosts', host_id=localhost.id))
        self.assertStatus(resp, 200, "expecting to find a host")
        data = json.loads(resp.get_data())
        assert data['name'] == localhost.name
        resp2: Response = client.delete(url_for('api.hosts', host_id=localhost.id))
        self.assertStatus(resp2, 204, "Should have been deleted")
        resp21: Response = client.delete(url_for('api.hosts', host_id=localhost.id))
        self.assertStatus(resp21, 404, "Should not exist")

        resp3: Response = client.get(url_for('api.hosts', host_id=localhost.id))
        self.assertStatus(resp3, 404, "expecting to not find a host")

    def test_host_update(self, client, localhost: Host, database):
        old_name = localhost.name
        resp: Response = client.put(url_for('api.hosts', host_id=localhost.id), data=dict(hostname='new_localhost',
                                                                                          name='new_localhost'))
        self.assertStatus(resp, 200, "expecting 200")
        database.session.refresh(localhost)
        assert localhost.hostname == 'new_localhost'
        assert old_name == localhost.name

    def assertStatus(self, resp, param, param1):
        assert resp.status_code == param, param1
