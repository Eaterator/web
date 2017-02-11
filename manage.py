from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from application.app import app, db
from management_commands.insert_base_data import insert_role_data, insert_source_data
from management_commands.insert_update_recipe_data import insert_scraper_data

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


@manager.command
def insert_recipe_data():
    insert_scraper_data()


if __name__ == '__main__':
    manager.run()
