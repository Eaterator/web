from application.auth.models import Role
from application.auth.roles import ROLES
from application.recipe.models import Source
from application.app import db


def insert_role_data():
    roles = [
        {
            'name': 'regular',
            'type_': 'consumer',
            'is_admin': False
        },
        {
            'name': 'corporate',
            'type_': 'business',
            'is_admin': False
        },
        {
            'name': 'admin',
            'type_': 'admin',
            'is_admin': True
        }
    ]

    if len(Role.query.all()) > 0:
        return
    for role in roles:
        new_role = Role(**role)
        db.session.add(new_role)
    db.session.commit()


def insert_source_data():
    sources = [
        {
            'base_url': 'foodnetwork.com',
            'name': 'Food Network'
        },
        {
            'base_url': 'epicurious.com',
            'name': 'Epicurious'
        },
        {
            'base_url': 'therecipedepository.com',
            'name': 'The Recipe Depository',
        },
        {
            'base_url': 'allrecipes.com',
            'name': 'All Recipes',
        }
    ]

    if len(Source.query.all()) > 0:
        return
    for source in sources:
        new_source = Source(**source)
        db.session.add(new_source)
    db.session.commit()
