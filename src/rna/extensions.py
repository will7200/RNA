import traceback

import flask
from celery import Celery
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from rna.modules import Base


celery = Celery()
celery.conf.task_routes = {
    'rna.modules.remote_management.host_executor.execute_host_command': {'queue': 'execute_host_command'},
}
celery.conf.update(task_track_started=True, accept_content=['json', 'yaml', 'msgpack'], result_extended=True)

db = SQLAlchemy(model_class=Base)

login_manager = LoginManager()
