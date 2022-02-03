import humanize
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from .utils import make_flake, hash_name


class GeneratorBaseModel(TimeStampedModel):

    id = models.PositiveBigIntegerField(
        primary_key=True, editable=False, default=make_flake
    )

    class Meta:
        abstract = True


class Media(GeneratorBaseModel):
    class Meta:
        verbose_name = _("Media Asset")

    name = models.CharField(
        verbose_name=_("filename"),
        blank=True,
        max_length=255,
        editable=False,
        help_text=_("Original filname from upload (untrusted)"),
    )
    file = models.FileField(
        verbose_name=_("file"),
        null=True,
        blank=True,
        upload_to=hash_name,
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

    def __str__(self):
        return self.name

    def filesize(self):
        return humanize.naturalsize(self.size, binary=True)

    def save(self, *args, **kwargs):
        """Intercept new file uploads"""
        new_upload = isinstance(self.file.file, UploadedFile)
        if new_upload:
            self.name = self.file.file.name
            self.type = self.file.file.content_type
            self.size = self.file.size
        super().save(*args, **kwargs)


class IsccCode(GeneratorBaseModel):
    class Meta:
        verbose_name = "ISCC Code"
        verbose_name_plural = "ISCC Codes"

    iscc = models.CharField(
        verbose_name="ISCC",
        max_length=73,
        blank=True,
        editable=False,
        help_text="International Standard Content Code",
    )

    name = models.CharField(
        verbose_name=_("name"),
        max_length=128,
        blank=True,
        help_text=_(
            "The title or name of the work manifested by the media asset. "
            "**Used as input for the ISCC Meta-Code**"
        ),
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True,
        max_length=4096,
        help_text=_(
            "Description of the digital content identified by the ISCC. "
            "**Used as input for the ISCC Meta-Code**"
        ),
    )

    metadata = models.JSONField(
        verbose_name=_("metadata"),
        null=True,
        blank=True,
        help_text=_(
            "Descriptive, industry-sector or use-case specific metadata. "
            "**Used as input for ISCC Meta-Code generation.**"
        ),
    )

    content = models.ForeignKey(
        verbose_name=_("content"),
        to="Media",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="iscc_code",
        help_text=_("The digital content that was used to create this ISCC."),
    )


class IsccTask(GeneratorBaseModel):
    class Meta:
        verbose_name = "ISCC Task"

    source_file = models.ForeignKey(
        verbose_name=_("Source File"),
        to="Media",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task",
        help_text=_("The media file used as source for ISCC generation."),
    )
    source_url = models.URLField(
        verbose_name=_("Source URL"),
        blank=True,
        help_text=_("URL of a the media file used as source for ISCC generation."),
    )
