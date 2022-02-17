from typing import Optional

from django.contrib import admin
from django import forms
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset
from django_q.tasks import async_task
from iscc_generator.models import IsccCode
from iscc_generator.tasks import create_iscc_code


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
        "iscc_monospaced",
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
        "iscc",
        "source_file",
        "source_url",
        "source_file_mediatype",
        "source_file_size",
        "name",
        "description",
        "metadata",
        "result",
    ]

    readonly_fields = [
        "iscc",
        "source_file_mediatype",
        "source_file_size",
        "source_file_name",
    ]

    formfield_overrides = {
        models.URLField: {"widget": forms.URLInput(attrs={"size": 98})},
        models.CharField: {"widget": forms.TextInput(attrs={"size": 98})},
        models.TextField: {"widget": forms.Textarea(attrs={"cols": 98, "rows": 8})},
        models.JSONField: {"widget": JSONEditorWidget(width="53em", height="28em")},
    }

    change_actions = ["action_create_iscc"]
    actions = ["action_create_iscc"]
    actions = ["action_create_iscc"]

    def save_model(self, request, obj, form, change):
        """Create ISCC on Save"""
        super().save_model(request, obj, form, change)
        create_iscc_code(obj.pk)

    def get_readonly_fields(self, request, obj: Optional[IsccCode] = None):
        if obj and obj.source_file:
            return super().get_readonly_fields(request, obj) + ["source_file"]
        return super().get_readonly_fields(request, obj)

    @takes_instance_or_queryset
    def action_create_iscc(self, request, queryset):
        for obj in queryset:
            async_task(create_iscc_code, obj.pk)

    action_create_iscc.label = "Generate ISCC"  # optional
    action_create_iscc.short_description = "Generate ISCC Codes for selected entries"
