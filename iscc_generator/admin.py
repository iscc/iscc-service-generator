from django.contrib import admin
from .models import Media, IsccCode, IsccTask


@admin.register(IsccCode)
class IsccCodeAdmin(admin.ModelAdmin):
    list_display = ("iscc", "name", "description", "metadata", "content", "created")


@admin.register(IsccTask)
class IsccTaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "type", "filesize", "created")
    readonly_fields = ("name", "type", "filesize")
    search_fields = ("name",)
    list_filter = ("type",)
