from flask import Blueprint

from rna.modules import register_blueprint

base_app = Blueprint("app", __name__)


@base_app.route('/health')
def version():
    return 'ok'


register_blueprint(base_app, url_prefix='/app')
