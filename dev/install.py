"""
Initialize a fresh installation

- creates the database
- import theme fixtures
- create demo user
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iscc_service_generator.settings")
from django.contrib.auth import get_user_model
from django.core import management
import django
import secrets

django.setup()


def migrate():
    management.call_command("migrate")


def create_demo_user(secure=True):
    User = get_user_model()
    if User.objects.filter(is_superuser=True):
        print("\n\nSuperuser already exists, skipped creating another one.")
        return
    username = "demo"
    if secure:
        password = secrets.token_hex(16)
    else:
        password = "demo"
    email = "demo@eexample.com"
    User.objects.create_superuser(username=username, password=password, email=email)
    print("\n\nCreated superuser!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Login at http://localhost:8000")
    print(f"Check interactive Rest API docs at http://localhost:8000/api/docs")


def install():
    migrate()
    create_demo_user(secure=True)


if __name__ == "__main__":
    install()
