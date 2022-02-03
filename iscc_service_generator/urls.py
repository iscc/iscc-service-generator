from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.apps import AuthConfig
from admin_interface.admin import Theme

# Override some defaults
AuthConfig.verbose_name = "Users"
admin.site.unregister(Theme)

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path("", admin.site.urls),
]
