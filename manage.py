from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from application.app import app, db
import management_commands

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def init_db():
    db.create_all()


@manager.command
def insert_base_data():
    management_commands.insert_role_data()
    management_commands.insert_source_data()


@manager.command
def insert_recipe_data():
    management_commands.insert_scraper_data()


@manager.command
def create_super_user_account():
    management_commands.create_super_user()


if __name__ == '__main__':
    manager.run()
