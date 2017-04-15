from application.auth.models import User, Role
from application.auth.controllers import PasswordUtilities, PasswordMismatchError
from application.base_models import db
from getpass import getpass


def create_super_user():
    admin_role = Role.query.filter_by(Role.type == 'admin').first()
    while True:
        username = input("Username: ")
        password = getpass("Password: ")
        confirm_password = getpass("Confirm Password: ")
        email = input("Email: ")
        first_name = input("First Name: ")
        last_name = input("Last Name: ")

        if password == confirm_password:
            try:
                password = PasswordUtilities.generate_password(password)
                new_user = User(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role=admin_role,
                )
                db.session.add(new_user)
                db.session.commit()
                print('\n Superuser added')
                return
            except PasswordMismatchError as e:
                print('\n\n Password mismatch or invalid format: {0}\n'.format(
                    str(e)
                ))
