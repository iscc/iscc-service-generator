import humanize
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from iscc_generator.base import GeneratorBaseModel
from iscc_generator.storage import get_storage_path
import iscc_sdk as idk


class IsccCode(GeneratorBaseModel):
    class Meta:
        verbose_name = "ISCC-CODE"
        verbose_name_plural = "ISCC-CODES"

    iscc = models.CharField(
        verbose_name="ISCC",
        max_length=73,
        blank=True,
        editable=False,
        db_index=True,
        help_text="International Standard Content Code",
    )

    source_file = models.ForeignKey(
        "Media",
        verbose_name=_("souce_file"),
        null=True,
        default=None,
        on_delete=models.CASCADE,
        help_text=_("File used for ISCC-CODE creation"),
    )

    source_url = models.URLField(
        verbose_name=_("source_url"),
        blank=True,
        default="",
        max_length=4096,
        help_text=_("URL of file used for generating the ISCC-CODE"),
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

    meta = models.TextField(
        verbose_name=_("meta"),
        default="",
        blank=True,
        max_length=16384,
        help_text=_(
            "Subject, industry, or use-case specific metadata, encoded as JSON string or Data-URL"
            " (used as sole input for Meta-Code and `metahash` generation if supplied)."
        ),
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
            return f"ISCC:{self.iscc}"
        return f"ISCC:{self.flake}"

    @admin.display(ordering="source_file__size", description="filesize")
    def source_file_size_human(self):
        if self.source_file:
            return humanize.naturalsize(self.source_file.size, binary=True)

    @admin.display(ordering="iscc", description="iscc")
    def iscc_monospaced(self):
        return format_html(
            f'<span style="font-family: monospace; font-weight: bold;">{self.iscc}</span>'
        )

    @admin.display(ordering="id", description="id")
    def flake_monospaced(self):
        return format_html(f'<span style="font-family: monospace">{self.flake}</span>')


class Media(GeneratorBaseModel):
    class Meta:
        verbose_name = _("Media Asset")

    name = models.CharField(
        verbose_name=_("filename"),
        blank=True,
        max_length=255,
        editable=False,
        help_text=_("Original filename from upload (untrusted)"),
    )
    source_file = models.FileField(
        verbose_name=_("file"),
        null=True,
        blank=True,
        upload_to=get_storage_path,
        help_text=_("The actual media asset"),
    )
    type = models.CharField(
        verbose_name=_("mediatype"),
        blank=True,
        max_length=255,
        editable=False,
        help_text=_("Original IANA Media Type (MIME type) from upload (untrusted)"),
    )
    size = models.PositiveBigIntegerField(
        verbose_name=_("filesize"),
        null=True,
        editable=False,
        help_text=_("The filesize of the media asset"),
    )

    metadata = models.JSONField(
        verbose_name=_("metadata"),
        null=True,
        blank=True,
        default=None,
        help_text=_("Metadata embedded in the file"),
    )

    original = models.ForeignKey(
        "self",
        verbose_name=_("original"),
        null=True,
        default=None,
        on_delete=models.CASCADE,
        help_text=_("Original media object if derived"),
    )

    def __str__(self):
        return self.name

    def filesize(self):
        if self.size:
            return humanize.naturalsize(self.size, binary=True)

    def save(self, *args, **kwargs):
        """
        Intercept new file uploads.

        Extract metadata before `source_file` eventually ends up in remote storage.
        """
        new_upload = False
        try:
            new_upload = isinstance(self.source_file.file, TemporaryUploadedFile)
        except ValueError:
            pass
        if new_upload:
            self.source_file.file.flush()
            self.name = self.source_file.file.name
            self.type = self.source_file.file.content_type
            self.size = self.source_file.size
            fp = self.source_file.file.temporary_file_path()
            mt, mode_ = idk.mediatype_and_mode(fp)
            if mode_ == "image":
                meta = idk.image_meta_extract(fp)
                self.metadata = meta
            elif mode_ == "audio":
                meta = idk.audio_meta_extract(fp)
                self.metadata = meta

        super().save(*args, **kwargs)
