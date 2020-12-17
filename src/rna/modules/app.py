from flask import Blueprint

from rna.modules import register_blueprint

base_app = Blueprint("app", __name__)

register_blueprint(base_app, url_prefix='/app')
