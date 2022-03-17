import humanize
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import models
from django.forms import model_to_dict
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
        null=True,
        blank=True,
        default=None,
        editable=False,
        db_index=True,
        help_text="International Standard Content Code",
    )

    source_file = models.ForeignKey(
        "Media",
        verbose_name=_("souce_file"),
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
        help_text=_("File used for ISCC-CODE creation"),
    )

    source_url = models.URLField(
        verbose_name=_("source_url"),
        null=True,
        blank=True,
        default=None,
        max_length=4096,
        help_text=_("URL of file used for generating the ISCC-CODE"),
    )

    name = models.CharField(
        verbose_name=_("name"),
        max_length=128,
        null=True,
        blank=True,
        default=None,
        help_text=_(
            "The title or name of the work manifested by the media asset. "
            "Used as input for the ISCC Meta-Code"
        ),
    )
    description = models.TextField(
        verbose_name=_("description"),
        null=True,
        blank=True,
        default=None,
        max_length=4096,
        help_text=_(
            "Description of the digital content identified by the ISCC. "
            "Used as input for the ISCC Meta-Code."
        ),
    )

    meta = models.TextField(
        verbose_name=_("meta"),
        null=True,
        blank=True,
        default=None,
        max_length=16384,
        help_text=_(
            "Subject, industry, or use-case specific metadata, encoded as JSON string or Data-URL"
            " (used as sole input for Meta-Code and `metahash` generation if supplied)."
        ),
    )

    creator = models.CharField(
        verbose_name=_("creator"),
        max_length=128,
        null=True,
        blank=True,
        default=None,
        help_text=_("An entity primarily responsible for making the resource."),
    )

    license = models.URLField(
        verbose_name=_("license"),
        null=True,
        blank=True,
        default=None,
        max_length=4096,
        help_text=_("URL of license for the digital content."),
    )

    acquire = models.URLField(
        verbose_name=_("acquire"),
        null=True,
        blank=True,
        default=None,
        max_length=4096,
        help_text=_("URL for acquiring a license for the digital content."),
    )

    result = models.JSONField(
        verbose_name=_("result"),
        null=True,
        blank=True,
        default=None,
        help_text=_("The result returned by the ISCC generator."),
    )

    def __str__(self):
        if self.iscc:
            return self.iscc
        return self.flake

    def get_metadata(self) -> idk.IsccMeta:
        """Returns embedable metadata as IsccMeta object"""
        data = model_to_dict(
            self, fields=("name", "description", "meta", "creator", "license", "aquire")
        )
        return idk.IsccMeta.parse_obj(data)

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
        null=True,
        blank=True,
        default=None,
        max_length=255,
        editable=False,
        help_text=_("Original filename from upload (untrusted)"),
    )
    source_file = models.FileField(
        verbose_name=_("file"),
        null=True,
        blank=True,
        default=None,
        upload_to=get_storage_path,
        help_text=_("The actual media asset"),
    )

    cid = models.CharField(
        verbose_name=_("cid"),
        null=True,
        blank=True,
        default=None,
        max_length=128,
        help_text=_("IPFS CIDv1"),
    )

    type = models.CharField(
        verbose_name=_("mediatype"),
        null=True,
        blank=True,
        default=None,
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
        blank=True,
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
            # TODO ipfs hashing may take long for large files - consider doing this in a worker
            self.cid = idk.ipfs_cidv1(fp)
            mt, mode_ = idk.mediatype_and_mode(fp)
            if mode_ == "image":
                meta = idk.image_meta_extract(fp)
                self.metadata = meta
            elif mode_ == "audio":
                meta = idk.audio_meta_extract(fp)
                self.metadata = meta

        super().save(*args, **kwargs)


class Nft(GeneratorBaseModel):
    class Meta:
        verbose_name = _("NFT")

    class Chain(models.TextChoices):
        PRIVATE = "PRIVATE"
        BITCOIN = "BITCOIN"
        ETHEREUM = "ETHEREUM"
        POLYGON = "POLYGON"

    iscc_code = models.ForeignKey(
        IsccCode,
        verbose_name=_("ISCC-CODE"),
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
        help_text=_("ISCC-CODE of NFT."),
    )

    chain = models.CharField(
        verbose_name=_("chain"),
        max_length=32,
        null=True,
        blank=True,
        default=None,
        choices=Chain.choices,
        help_text=_("The blockchain on which the ISCC-CODE will be declared."),
    )

    wallet = models.CharField(
        verbose_name=_("wallet"),
        max_length=128,
        null=True,
        blank=True,
        default=None,
        help_text=_("The wallet-address that will sign the ISCC declaration."),
    )

    attributes = models.JSONField(
        verbose_name=_("attributes"),
        null=True,
        blank=True,
        default=None,
        help_text=_("NFT attributes to be shown on marketplaces."),
    )

    external_url = models.URLField(
        verbose_name=_("external url"),
        null=True,
        blank=True,
        default=None,
        max_length=4096,
        help_text=_("External URL to be shown on marketplaces."),
    )

    redirect = models.URLField(
        verbose_name=_("redirect"),
        null=True,
        blank=True,
        default=None,
        max_length=4096,
        help_text=_(
            "URL to which an ISCC resolver should redirect for the registered ISCC-ID."
        ),
    )

    original = models.BooleanField(
        verbose_name=_("original"),
        null=True,
        blank=True,
        default=None,
        help_text=_(
            "Whether the signee claims to be the original creator of the digital content."
        ),
    )

    verifications = models.JSONField(
        verbose_name=_("verifications"),
        null=True,
        blank=True,
        default=None,
        help_text=_(
            "A list of self-verifications (Public URLs under the authority of the signee."
        ),
    )

    result = models.JSONField(
        verbose_name=_("result"),
        null=True,
        blank=True,
        default=None,
        help_text=_("The result returned by the NFT generator."),
    )

    def __str__(self):
        return f"NFT-{self.flake}"

    def patch(self) -> dict:
        """Return data used for patching ISCC Metadata"""
