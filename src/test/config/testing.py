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
        "always_eager"               : True,  # noqa: E203
        "eager_propagates_exceptions": True,  # noqa: E203
        "result_backend"             : "cache",  # noqa: E203
        "cache_backend"              : "memory",  # noqa: E203
    }
