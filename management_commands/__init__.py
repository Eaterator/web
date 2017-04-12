from management_commands.create_super_user import create_super_user
from management_commands.insert_base_data import insert_role_data, insert_source_data
from management_commands.insert_update_recipe_data import insert_scraper_data, clean_recipe_data, \
    create_fulltext_recipe_fields
from management_commands.collect_static import collect_static


def create_indexes(db, drop_index=False):
    """
    Creates all indexes on models in project if they do not exists already. Assumes all models
    inherit from RequiredFields class, otherwise will need to adjust search for subclasses. If the index
    exists SQLAlchemy throws an error and we assume everything is ok.
    :param db: The app db object, acts as the engine param for the Index.create()
    :param drop_index: specifies whether the indexes should be dropped or created
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
                        if not drop_index:
                            item.create(db.engine)
                        else:
                            item.drop(db.engine)
                    except ProgrammingError:  # If index exists, creation fails on error
                        pass
    return
