from django.contrib import admin
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset
from iscc_generator.models import IsccCode
from iscc_generator.tasks import create_iscc_code


@admin.register(IsccCode)
class IsccCodeAdmin(DjangoObjectActions, admin.ModelAdmin):
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

    @takes_instance_or_queryset
    def action_create_iscc(self, request, queryset):
        for obj in queryset:
            create_iscc_code(obj.id)

    action_create_iscc.label = "Generate ISCC"  # optional
    action_create_iscc.short_description = "(Re)generate ISCC code"

    change_actions = ["action_create_iscc"]
    changelist_actions = ["action_create_iscc"]
    actions = ["action_create_iscc"]
