from typing import Optional

from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset
from django_q.tasks import async_task

from iscc_generator.models import IsccCode
from iscc_generator.tasks import create_iscc_code, download_file


@admin.register(IsccCode)
class IsccCodeAdmin(DjangoObjectActions, admin.ModelAdmin):

    actions_on_top = False
    actions_on_bottom = True

    search_fields = [
        "iscc",
        "source_file_name",
        "name",
    ]

    list_display = [
        "id",
        "iscc",
        "source_file_name",
        "name",
        "source_file_mediatype",
        "source_file_size_human",
        "created",
    ]
    list_filter = [
        "source_file_mediatype",
    ]

    fields = [
        "source_file",
        "source_url",
        "source_file_mediatype",
        "source_file_size",
        "name",
        "description",
        "result",
    ]

    readonly_fields = ["iscc", "source_file_mediatype", "source_file_size"]

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }

    def get_readonly_fields(self, request, obj: Optional[IsccCode] = None):
        if obj and obj.source_file:
            return super().get_readonly_fields(request, obj) + ["source_file"]
        return super().get_readonly_fields(request, obj)

    @takes_instance_or_queryset
    def action_create_iscc(self, request, queryset):
        for obj in queryset:
            async_task(create_iscc_code, obj.pk)

    action_create_iscc.label = "Regenerate ISCC"  # optional
    action_create_iscc.short_description = "Regenerate selected ISCC Codes"

    change_actions = ["action_create_iscc"]
    # changelist_actions = ["action_create_iscc"]
    actions = ["action_create_iscc"]
