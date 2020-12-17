from flask import Blueprint

from . import register_blueprint

api = Blueprint("api", __name__)


@api.route('/api/version')
def version():
    return 'v1'


register_blueprint(api, url_prefix='/api/v1')
