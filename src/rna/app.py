import base64
import os

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

import modules.auth.routes  # noqa
import modules.users.routes  # noqa
from extensions import db, login_manager
from modules import get_registered_blueprints
from modules.users.model import User, Role
from modules.users.routes import users_service


def create_app(config):
    app: Flask = Flask("RNA", template_folder=os.path.join(os.path.dirname(__file__), "templates"))
    app.url_map.strict_slashes = False
    app.config.update(**os.environ)
    if isinstance(config, object):
        app.config.from_object(config)
    for bp in get_registered_blueprints():
        blueprint, kwargs = bp
        app.register_blueprint(blueprint, **kwargs)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        try:
            user = User(username="admin", email="email@example.com")
            user.set_password("password")
            user.roles.append(Role(name='admin'))
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            pass

    # pycharm is acting weird here
    # noinspection PyTypeChecker
    login_manager.init_app(app)
    configure_app(app)
    return app


def configure_app(app):
    @app.route('/')
    @login_required
    def index():
        return render_template("index.html")

    @login_manager.user_loader
    def load_user(user_id):
        return users_service.get_user(user_id)

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect(f'{url_for("app.login")}?next=' + request.path)

    @login_manager.request_loader
    def load_user_from_request(r):
        # first, try to login using the api_key url arg
        # api_key = request.args.get('api_key')
        # if api_key:
        #     user = User.query.filter_by(api_key=api_key).first()
        #     if user:
        #         return user

        # next, try to login using Basic Auth
        api_key = r.headers.get('Authorization')
        if api_key:
            api_key = api_key.replace('Basic ', '', 1)
            try:
                api_key = base64.b64decode(api_key)
            except TypeError:
                pass
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        # finally, return None if both methods did not login the user
        return None


if __name__ == '__main__':
    load_dotenv()

    create_app(None).run()
