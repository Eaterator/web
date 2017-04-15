from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from application.base_models import db
from application.app import create_app
import management_commands

app = create_app()
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
    """
    :param delete: whether to delete.
    # N.B. if having issues with the index on ingredient recipe, old insertion allowed
    # duplicated ingredients. to fix:
    DELETE FROM ingredient_recipe
    WHERE pk IN (
      SELECT sq.ir_pk FROM
      (SELECT MIN(pk) ir_pk, recipe, ingredient
      FROM ingredient_recipe
      GROUP BY recipe, ingredient
      HAVING COUNT(ingredient) > 1) sq
    )
    N.B. will need to run multiple times! only deletes one duplicate per iteration!!
    :return:
    """
    drop_indexes = True if delete else False
    management_commands.create_indexes(db, drop_index=drop_indexes)


if __name__ == '__main__':
    manager.run()
