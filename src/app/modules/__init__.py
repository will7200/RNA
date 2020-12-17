from typing import List, Tuple, Any, Dict

_registered_blueprints = []


def register_blueprint(blueprint, **options):
    """Register a :class:`~flask.Blueprint` on the application. Keyword
    arguments passed to this method will override the defaults set on the
    blueprint.

    Calls the blueprint's :meth:`~flask.Blueprint.register` method after
    recording the blueprint in the application's :attr:`blueprints`.

    :param blueprint: The blueprint to register.
    :param url_prefix: Blueprint routes will be prefixed with this.
    :param subdomain: Blueprint routes will match on this subdomain.
    :param url_defaults: Blueprint routes will use these default values for
        view arguments.
    :param options: Additional keyword arguments are passed to
        :class:`~flask.blueprints.BlueprintSetupState`. They can be
        accessed in :meth:`~flask.Blueprint.record` callbacks.

    .. versionadded:: 0.7
    """
    _registered_blueprints.append((blueprint, options))


def get_registered_blueprints() -> List[Tuple[Any, Dict[str, Any]]]:
    return _registered_blueprints


from werkzeug.local import LocalProxy
from flask import current_app

logger = LocalProxy(lambda: current_app.logger)

from .api import api
from .app import base_app
from .models import Base, UpdateMixin

__all__ = [
    # Classes
    'Base',
    'UpdateMixin',
    # rest
    'api',
    'get_registered_blueprints',
    'register_blueprint',
    "logger"
]
