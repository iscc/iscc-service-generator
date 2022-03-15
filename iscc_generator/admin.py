from typing import Optional

import humanize
from django.contrib import admin
from django import forms
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from django_object_actions import DjangoObjectActions, takes_instance_or_queryset
from django_q.tasks import async_task
from iscc_generator.models import IsccCode, Media, Nft
from iscc_generator.tasks import iscc_generator_task


@admin.register(Nft)
class NftAdmin(admin.ModelAdmin):
    list_display = (
        "flake",
        "iscc_code",
        "chain",
        "wallet",
        "original",
    )

    formfield_overrides = {
        models.URLField: {"widget": forms.URLInput(attrs={"size": 98})},
        models.CharField: {"widget": forms.TextInput(attrs={"size": 98})},
        models.TextField: {"widget": forms.Textarea(attrs={"cols": 98, "rows": 8})},
        models.JSONField: {
            "widget": JSONEditorWidget(
                width="53em", height="18em", options={"mode": "view"}
            )
        },
    }


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = (
        "flake",
        "name",
        "source_file",
        "type",
        "filesize",
        "created",
        "original_flake",
    )

    fields = (
        "flake",
        "original_flake",
        "name",
        "source_file",
        "type",
        "filesize",
        "metadata",
    )
    readonly_fields = ("flake", "original_flake", "name", "type", "filesize")
    search_fields = ("source_file",)
    list_filter = ("type",)

    formfield_overrides = {
        models.JSONField: {
            "widget": JSONEditorWidget(
                width="53em", height="28em", options={"mode": "view"}
            )
        },
    }

    @admin.display(description="original")
    def original_flake(self, obj):
        if obj.original:
            return obj.original.flake


@admin.register(IsccCode)
class IsccCodeAdmin(DjangoObjectActions, admin.ModelAdmin):

    actions_on_top = False
    actions_on_bottom = True

    list_display = (
        "flake_monospaced",
        "iscc_monospaced",
        "filename",
        "mediatype",
        "filesize",
        "created",
    )
    search_fields = (
        "iscc",
        "source_file__name",
        "name",
    )

    list_filter = ("source_file__type",)
    readonly_fields = ("iscc",)
    fields = (
        "iscc",
        "source_file",
        "source_url",
        "name",
        "description",
        "meta",
        "result",
    )
    formfield_overrides = {
        models.URLField: {"widget": forms.URLInput(attrs={"size": 98})},
        models.CharField: {"widget": forms.TextInput(attrs={"size": 98})},
        models.TextField: {"widget": forms.Textarea(attrs={"cols": 98, "rows": 8})},
        models.JSONField: {
            "widget": JSONEditorWidget(
                width="53em", height="28em", options={"mode": "view"}
            )
        },
    }

    @admin.display(ordering="source_file__name")
    def filename(self, obj):
        if obj.source_file:
            return obj.source_file.name

    @admin.display(ordering="source_file__type")
    def mediatype(self, obj):
        if obj.source_file:
            return obj.source_file.type

    @admin.display(ordering="source_file__size")
    def filesize(self, obj):
        if obj.source_file:
            return humanize.naturalsize(obj.source_file.size, binary=True)

    change_actions = ["action_create_iscc"]
    actions = ["action_create_iscc"]

    def save_model(self, request, obj, form, change):
        """Create ISCC on Save"""
        super().save_model(request, obj, form, change)
        iscc_generator_task(obj.pk)

    @takes_instance_or_queryset
    def action_create_iscc(self, request, queryset):
        for obj in queryset:
            async_task(iscc_generator_task, obj.pk)

    action_create_iscc.label = "Generate ISCC"  # optional
    action_create_iscc.short_description = "Generate ISCC Codes for selected entries"
