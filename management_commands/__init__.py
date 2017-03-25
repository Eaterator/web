from management_commands.create_super_user import create_super_user
from management_commands.insert_base_data import insert_role_data, insert_source_data
from management_commands.insert_update_recipe_data import insert_scraper_data, clean_recipe_data


def create_indexes(db):
    """
    Creates all indexes on models in project if they do not exists already. Assumes all models
    inherit from RequiredFields class, otherwise will need to adjust search for subclasses.
    :param db: The app db object, acts as the engine param for the Index.create()
    :return:
    """
    from application.base_models import RequiredFields
    from sqlalchemy import Index
    from sqlalchemy.exc import ProgrammingError
    for klass in RequiredFields.__subclasses__():
        if hasattr(klass, '__table_args__'):
            for item in getattr(klass, '__table_args__'):
                if isinstance(item, Index):
                    try:
                        item.create(db.engine)
                    except ProgrammingError:  # If index exists, creation fails on error
                        pass
    return
