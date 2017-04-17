from application.auth.models import Role
from application.recipe.models import Source
from application.base_models import db


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
        },
        {
            'base_url': 'bonappetit.com',
            'name': 'Bon Appetit'
        },
        {
            'base_url': 'food.com',
            'name': 'Food'
        },
        {
            'base_url': 'simplyrecipes.com',
            'name': 'Simply Recipes'
        },
        {
            'base_url': 'bbcgoodfood.com',
            'name': 'BBC Good Food'
        },
        {
            'base_url': 'williams-sonoma.com',
            'name': 'Williams Sonoma'
        },
        {
            'base_url': 'finedininglovers.com',
            'name': 'Fine Dining Lovers'
        },
        {
            'base_url': 'thekitchn.com',
            'name': 'The Kitchn'
        },
        {
            'base_url': 'chowhound.com',
            'name': 'Chow'
        },
        {
            'base_url': 'myrecipes.com',
            'name': 'My Recipes'
        },
        {
            'base_url': '',
            'name': 'Other'
        }
    ]

    for source in sources:
        exists = Source.query.filter(Source.name == source['name']).all()
        if len(exists) <= 0:
            new_source = Source(**source)
            db.session.add(new_source)
    db.session.commit()
