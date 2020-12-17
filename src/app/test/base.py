import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase

from modules import get_registered_blueprints
from database import db


class TestBaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'something')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_ECHO = False


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app = Flask("Computer Management")
        app.config.from_object(TestBaseConfig())
        app.url_map.strict_slashes = False
        for bp in get_registered_blueprints():
            blueprint, kwargs = bp
            app.register_blueprint(blueprint, **kwargs)
        # don't have to store the variable anywhere since the context will have the correct db
        SQLAlchemy(app)
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
