"""Script to handle database migrations"""
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from rna.app import create_app
from rna.extensions import db

app = create_app(None)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
