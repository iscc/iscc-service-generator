import humanize
from blake3 import blake3
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.utils.html import format_html
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from .utils import make_flake


class GeneratorBaseModel(TimeStampedModel):

    id = models.PositiveBigIntegerField(
        primary_key=True, editable=False, default=make_flake
    )

    class Meta:
        abstract = True


def hash_name(instance, filename):
    hasher = blake3()
    for chunk in instance.source_file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest() + "/" + filename


class IsccCode(GeneratorBaseModel):
    class Meta:
        verbose_name = "ISCC Code"
        verbose_name_plural = "ISCC Codes"

    iscc = models.CharField(
        verbose_name="ISCC",
        max_length=73,
        blank=True,
        editable=False,
        db_index=True,
        help_text="International Standard Content Code",
    )

    source_file = models.FileField(
        verbose_name=_("source file"),
        blank=True,
        default="",
        upload_to=hash_name,
        help_text=_("The file used for generating the ISCC"),
    )

    source_file_name = models.CharField(
        verbose_name=_("filename"),
        blank=True,
        max_length=255,
        default="",
        editable=False,
        help_text=_("Original filename from upload (autoset / untrusted)"),
    )

    source_file_mediatype = models.CharField(
        verbose_name=_("mediatype"),
        blank=True,
        max_length=255,
        default="",
        editable=False,
        help_text=_(
            "Original IANA Media Type (MIME type) from upload (autoset / untrusted)"
        ),
    )

    source_file_size = models.PositiveBigIntegerField(
        verbose_name=_("filesize"),
        null=True,
        editable=False,
        default=0,
        help_text=_("The filesize of the media asset"),
    )

    source_url = models.URLField(
        verbose_name=_("source_url"),
        blank=True,
        default="",
        max_length=4096,
        help_text=_("URL of file used for generating the ISCC"),
    )

    name = models.CharField(
        verbose_name=_("name"),
        max_length=128,
        default="",
        blank=True,
        help_text=_(
            "The title or name of the work manifested by the media asset. "
            "Used as input for the ISCC Meta-Code"
        ),
    )
    description = models.TextField(
        verbose_name=_("description"),
        default="",
        blank=True,
        max_length=4096,
        help_text=_(
            "Description of the digital content identified by the ISCC. "
            "Used as input for the ISCC Meta-Code"
        ),
    )

    metadata = models.JSONField(
        verbose_name=_("metadata"),
        null=True,
        blank=True,
        default=None,
        help_text=_("Metadata for Meta-Code"),
    )

    embed = models.JSONField(
        verbose_name=_("embed"),
        null=True,
        blank=True,
        default=None,
        help_text=_("Fields for embedding"),
    )

    result = models.JSONField(
        verbose_name=_("result"),
        null=True,
        blank=True,
        default=None,
        help_text=_("The result returned by the ISCC generator"),
    )

    def __str__(self):
        if self.iscc:
            return f"{self.source_file_name} - ISCC:{self.iscc}"
        return self.source_file_name

    @admin.display(ordering="source_file_size", description="filesize")
    def source_file_size_human(self):
        if self.source_file_size:
            return humanize.naturalsize(self.source_file_size, binary=True)

    @admin.display(ordering="iscc", description="iscc")
    def iscc_monospaced(self):
        return format_html(f'<span style="font-family: monospace">{self.iscc}</span>')

    def save(self, *args, **kwargs):
        """Intercept new file uploads to set file properties and trigger ISCC processing"""
        if self.source_file:
            new_upload = isinstance(self.source_file.file, UploadedFile)
            if new_upload:
                self.source_file_name = self.source_file.file.name
                self.source_file_mediatype = self.source_file.file.content_type
                self.source_file_size = self.source_file.size
        super().save(*args, **kwargs)
