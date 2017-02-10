import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from management_commands.insert_base_data import insert_role_data, insert_source_data

from app.run import app, db

app.config.from_object(os.environ['APP_SETTINGS'])
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def init_db():
    db.create_all()


@manager.command
def insert_base_data():
    insert_role_data()
    insert_source_data()

if __name__ == '__main__':
    manager.run()
