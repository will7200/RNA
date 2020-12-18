from celery import Celery
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from rna.modules import Base

db = SQLAlchemy(model_class=Base)

login_manager = LoginManager()

# Celery
celery = Celery("worker")

celery.conf.update(task_track_started=True, accept_content=['json', 'yaml', 'msgpack'], result_extended=True)
