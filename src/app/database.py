from flask_sqlalchemy import SQLAlchemy

from modules import Base

db = SQLAlchemy(model_class=Base)
