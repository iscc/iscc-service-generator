"""
Runs django.db.connection.ensure_connection() and exists with 0 with the connection is established.
"""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iscc_service_generator.settings")

import django
import django.db
from django.db.utils import OperationalError

django.setup()


if __name__ == "__main__":
    try:
        django.db.connection.ensure_connection()
    except (OperationalError):
        sys.exit(-1)
    sys.exit(0)
