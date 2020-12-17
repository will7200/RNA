from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from rna.modules import Base

db = SQLAlchemy(model_class=Base)

login_manager = LoginManager()

