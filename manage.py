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
def delete_recipe_data():
    management_commands.clean_recipe_data()
    management_commands.create_indexes(db, drop_index=True)


@manager.command
def create_super_user_account():
    management_commands.create_super_user()


@manager.command
def create_fulltext_fields():
    management_commands.create_fulltext_recipe_fields()
    management_commands.create_indexes(db, drop_index=True)
    management_commands.create_indexes(db)


@manager.command
def collect_static():
    management_commands.collect_static()


@manager.option('-d', '--delete', dest='delete', default=None)
def create_indexes(delete):
    drop_indexes = True if delete else False
    management_commands.create_indexes(db, drop_index=drop_indexes)


if __name__ == '__main__':
    manager.run()
