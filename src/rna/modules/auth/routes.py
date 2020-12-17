# manage
from rna.modules.app import base_app
from rna.modules.auth.authentication import authenticator_service
from rna.modules.auth.views import Login, Logout
from rna.modules.users.routes import users_service

login_controller = Login.as_view('login', users_service=users_service, authenticator=authenticator_service)
base_app.add_url_rule('/login', methods=['GET', 'POST'], view_func=login_controller)

logout_controller = Logout.as_view('logout')
base_app.add_url_rule('/logout', methods=['GET'], view_func=logout_controller)
