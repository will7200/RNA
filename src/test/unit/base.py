import os

from flask_testing import TestCase

from rna.extensions import db


class TestBaseConfig:
    """Base configuration."""
    LOGIN_DISABLED = False
    SERVER_NAME = "localhost:5000"
    SECRET_KEY = os.getenv('SECRET_KEY', 'something')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_ECHO = False


class BaseTestCase(TestCase):
    """ Base Tests """

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
