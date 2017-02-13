from application.auth.models import Role
from application.recipe.models import Source
from application.app import db


def insert_role_data():
    roles = [
        {
            'name': 'regular',
            'type': 'consumer',
            'admin': False
        },
        {
            'name': 'corporate',
            'type': 'business',
            'admin': False
        },
        {
            'name': 'admin',
            'type': 'admin',
            'admin': True
        }
    ]
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
    for source in sources:
        new_source = Source(**source)
        db.session.add(new_source)
    db.session.commit()
