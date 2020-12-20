import base64
import os

from flask import Flask, redirect, request, url_for
from sqlalchemy.exc import IntegrityError

import rna.modules.auth.routes  # noqa
import rna.modules.remote_management.routes  # noqa
import rna.modules.users.routes  # noqa
from rna.extensions import db, login_manager, celery
from rna.modules import get_registered_blueprints
from rna.modules.remote_management.host_executor import execute_host_command
from rna.modules.remote_management.models import Host
from rna.modules.users.model import User, Role
from rna.modules.users.routes import users_service


class DefaultConfig(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    # Celery
    CELERY_CONFIG = {
        "broker_url"                 : "sqla+sqlite:///celerydb.db",  # noqa
        "cache_backend"              : "db+sqlite:///celerydb.db",  # noqa
        "always_eager"               : False,  # noqa
        "eager_propagates_exceptions": True,  # noqa
        "result_backend"             : "db+sqlite:///celerydb.db",  # noqa
        # "broker_transport_options"   : {'max_retries': 1},
    }


def create_app(config):
    app: Flask = Flask("RNA", template_folder=os.path.join(os.path.dirname(__file__), "templates"),
                       static_folder=os.path.join(os.path.dirname(__file__), "static"))
    app.url_map.strict_slashes = False
    app.config.from_object(DefaultConfig())
    app.config.update(**os.environ)
    db.init_app(app)
    celery.conf.update(app.config.get("CELERY_CONFIG"))
    if isinstance(config, object):
        app.config.from_object(config)
    for bp in get_registered_blueprints():
        blueprint, kwargs = bp
        app.register_blueprint(blueprint, **kwargs)

    # pycharm is acting weird here
    # noinspection PyTypeChecker
    login_manager.init_app(app)
    configure_app(app)
    return app


def make_celery(app=None):
    app = app or create_app(None)
    celery.conf.update(app.config['CELERY_CONFIG'])
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def configure_app(app):
    @app.route('/')
    def index():
        return redirect(url_for("app.hosts"))

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
