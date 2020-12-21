import json

import pytest
from flask import url_for
from werkzeug import Response

from rna.modules.remote_management.models import Host, decrypt_aes_gcm


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

    def test_host_creation(self, client, database):
        resp: Response = client.post(url_for('api.hosts'), data=dict(
            name='created_hostname', hostname='created_hostname',
        ))
        self.assertStatus(resp, 201, "expecting 201")
        data = json.loads(resp.get_data())
        assert data['name'] == 'created_hostname'
        new_host = Host.query.get(data['id'])
        assert new_host.name == 'created_hostname'

    def test_host_creation_encrypted_missing_password(self, client):
        resp: Response = client.post(url_for('api.hosts'), data=dict(
            name='created_hostname', hostname='created_hostname',
            password='password', authentication_method="password",
            encrypt_authentication=True
        ))
        self.assertStatus(resp, 400, "expecting 400")

    def test_host_creation_encrypted(self, client, database):
        resp: Response = client.post(url_for('api.hosts'), data=dict(
            name='created_hostname', hostname='created_hostname',
            password='password', authentication_method="password",
            encrypt_authentication=True, user_password='password_encrypt'
        ))
        self.assertStatus(resp, 201, "expecting 201")
        data = json.loads(resp.get_data())
        assert data['name'] == 'created_hostname'
        new_host: Host = Host.query.get(data['id'])
        assert new_host.name == 'created_hostname'

        # check password field to make sure its encrypted
        assert new_host.password != 'password'
        assert 'password'.encode('utf8') == decrypt_aes_gcm(new_host.password, 'password_encrypt'.encode('utf-8'))

    def test_another_user_cant_get_another_users_host(self, authenticated_power_user, client, database,
                                                      admin_user, power_user):
        resp1: Response = client.post(url_for('api.hosts'), data=dict(
            name='created_hostname', hostname='created_hostname',
        ))
        self.assertStatus(resp1, 201, "expecting 201")
        data1 = json.loads(resp1.get_data())
        assert data1['name'] == 'created_hostname'
        resp2: Response = authenticated_power_user.post(url_for('api.hosts'), data=dict(
            name='created_hostname', hostname='created_hostname',
        ))
        data2 = json.loads(resp2.get_data())
        assert data2['name'] == 'created_hostname'
        self.assertStatus(resp2, 201, "expecting 201")

        # test admin user
        resp: Response = client.get(url_for('api.hosts', host_id=data1['id']))
        assert resp.status_code == 200, "Expecting a host"

        # admin now try to get power users host
        resp: Response = client.get(url_for('api.hosts', host_id=data2['id']))
        assert resp.status_code == 404, "Expecting to not find a host"

        # test power user
        resp: Response = authenticated_power_user.get(url_for('api.hosts', host_id=data2['id']))
        assert resp.status_code == 200, "Expecting a host"

        resp: Response = authenticated_power_user.get(url_for('api.hosts', host_id=data1['id']))
        assert resp.status_code == 404, "Expecting to not find a host"

    def assertStatus(self, resp, param, param1):
        assert resp.status_code == param, param1
