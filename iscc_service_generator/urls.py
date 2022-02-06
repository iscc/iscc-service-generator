from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .api_v1 import api


urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path("api/", api.urls),
    path("", admin.site.urls),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns = staticfiles_urlpatterns() + urlpatterns
