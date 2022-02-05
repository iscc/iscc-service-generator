from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.apps import AuthConfig
from admin_interface.admin import Theme
from django_q.apps import DjangoQConfig
from constance.apps import ConstanceConfig

from .api_v1 import api

# Override some defaults
AuthConfig.verbose_name = "Users"
DjangoQConfig.verbose_name = "Tasks"
ConstanceConfig.verbose_name = "Settings"
admin.site.unregister(Theme)

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path("api/", api.urls),
    path("", admin.site.urls),
]
