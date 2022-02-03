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

django.setup()


def migrate():
    management.call_command("makemigrations")
    management.call_command("migrate")


def load_fixtures():
    management.call_command(
        "loaddata", "--app", "admin_interface.Theme", "admin_interface_theme_iscc"
    )


def create_demo_user():
    User = get_user_model()
    if User.objects.exists():
        return
    username = "demo"
    password = "demo"
    email = "demo@eexample.com"
    User.objects.create_superuser(username=username, password=password, email=email)


def install():
    migrate()
    load_fixtures()
    create_demo_user()
    print(
        "\n\nISCC Generator Service installed successfully.\n"
        '- Start development server with "python manage.py runserver".\n'
        '- Login to dashboard at http://127.0.0.1:8000 with user "demo" and password "demo"'
    )


if __name__ == "__main__":
    install()
