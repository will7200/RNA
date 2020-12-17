import pytest
from flask import url_for
from werkzeug import Response

from rna.modules.auth.authentication import DBAuthentication
from rna.modules.core.users.models import UserDoesntExist


class TestDBAuthentication(object):
    auth = DBAuthentication()

    def test_authenticate_correct_password(self, admin_user):
        assert self.auth.authenticate(admin_user.username, "password") is True
        assert self.auth.authenticate(admin_user, "password") is True

    def test_authentication_wrong_password(self, admin_user):
        assert self.auth.authenticate(admin_user.username, "something_wrong") is False

    def test_auth_no_user(self):
        with pytest.raises(UserDoesntExist):
            self.auth.authenticate("invalid_user", "invalid_password")


class TestAuthenticationControllers(object):
    @pytest.fixture(autouse=True)
    def _client(self, application):
        self.client = application.test_client()

    def test_login_password_not_set(self):
        resp: Response = self.client.post(url_for('app.login'), data=dict(username='test_admin', password=''))
        assert resp.status_code == 400

    def test_login_no_user(self):
        resp: Response = self.client.post(url_for('app.login'), data=dict(username='test_admin', password='password'))
        assert resp.status_code == 401

    def test_login(self, admin_user):
        resp: Response = self.client.post(url_for('app.login'), data=dict(username='test_admin', password='password'))
        assert resp.status_code == 302

    def test_login_bad_password(self, admin_user):
        resp: Response = self.client.post(url_for('app.login'), data=dict(username='test_admin', password='password1'))
        assert resp.status_code == 401

    def test_login_invalid_user(self, invalid_user):
        resp: Response = self.client.post(url_for('app.login'),
                                          data=dict(username=invalid_user.username, password='password'))
        assert resp.status_code == 401

    def test_login_bad_next_link(self, admin_user):
        resp: Response = self.client.post(f"{url_for('app.login')}?next=http://bad_domain.com/",
                                          data=dict(username='test_admin', password='password'))
        assert resp.status_code == 400

    def test_login_page_redirect_on_authenticated_user(self, admin_user):
        resp: Response = self.client.post(url_for('app.login'),
                                          data=dict(username=admin_user.username, password='password'))
        assert resp.status_code == 302
        resp: Response = self.client.get(url_for('app.login'))
        assert resp.status_code == 302

    def test_login_get_page(self, admin_user):
        resp: Response = self.client.get(url_for('app.login'))
        assert resp.status_code == 200

    def test_logout_authenticated_user(self, admin_user):
        resp: Response = self.client.post(url_for('app.login'),
                                          data=dict(username=admin_user.username, password='password'))
        assert resp.status_code == 302
        resp: Response = self.client.get(url_for('app.logout'))
        assert resp.status_code == 302

    def test_logout_anonymous_user(self, admin_user):
        resp: Response = self.client.get(url_for('app.logout'))
        assert resp.status_code == 302
