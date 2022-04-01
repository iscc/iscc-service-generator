"""
ASGI config for iscc_service_generator project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.conf import settings
from django.core.asgi import get_asgi_application
from asgi_middleware_static_file import ASGIMiddlewareStaticFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iscc_service_generator.settings")

application = get_asgi_application()

if not settings.DEBUG:
    application = ASGIMiddlewareStaticFile(
        application,
        static_url=settings.STATIC_URL,
        static_root_paths=[settings.STATIC_ROOT],
    )
