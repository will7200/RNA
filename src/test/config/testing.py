import os


class TestBaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'something')
    DEBUG = False
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ECHO = False

    PRESERVE_CONTEXT_ON_EXCEPTION = False

    CELERY_CONFIG = {
        "always_eager"               : True,
        "eager_propagates_exceptions": True,
        "result_backend"             : "cache",
        "cache_backend"              : "memory",
    }
