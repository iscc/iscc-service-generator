# Generated by Django 4.0.3 on 2022-03-18 16:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import iscc_generator.base
import iscc_generator.storage
import model_utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Media",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    models.PositiveBigIntegerField(
                        default=iscc_generator.base.make_flake,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        default=None,
                        editable=False,
                        help_text="Original filename from upload (untrusted)",
                        max_length=255,
                        null=True,
                        verbose_name="filename",
                    ),
                ),
                (
                    "source_file",
                    models.FileField(
                        blank=True,
                        default=None,
                        help_text="The actual media asset",
                        null=True,
                        upload_to=iscc_generator.storage.get_storage_path,
                        verbose_name="file",
                    ),
                ),
                (
                    "cid",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text="IPFS CIDv1",
                        max_length=128,
                        null=True,
                        verbose_name="cid",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        blank=True,
                        default=None,
                        editable=False,
                        help_text="Original IANA Media Type (MIME type) from upload (untrusted)",
                        max_length=255,
                        null=True,
                        verbose_name="mediatype",
                    ),
                ),
                (
                    "size",
                    models.PositiveBigIntegerField(
                        editable=False,
                        help_text="The filesize of the media asset",
                        null=True,
                        verbose_name="filesize",
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="Metadata embedded in the file",
                        null=True,
                        verbose_name="metadata",
                    ),
                ),
                (
                    "original",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        help_text="Original media object if derived",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="iscc_generator.media",
                        verbose_name="original",
                    ),
                ),
            ],
            options={
                "verbose_name": "Media Asset",
            },
        ),
        migrations.CreateModel(
            name="Nft",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    models.PositiveBigIntegerField(
                        default=iscc_generator.base.make_flake,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "chain",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("PRIVATE", "Private"),
                            ("BITCOIN", "Bitcoin"),
                            ("ETHEREUM", "Ethereum"),
                            ("POLYGON", "Polygon"),
                        ],
                        default=None,
                        help_text="The blockchain on which the ISCC-CODE will be declared.",
                        max_length=32,
                        null=True,
                        verbose_name="chain",
                    ),
                ),
                (
                    "wallet",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text="The wallet-address that will sign the ISCC declaration.",
                        max_length=128,
                        null=True,
                        verbose_name="wallet",
                    ),
                ),
                (
                    "attributes",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="NFT attributes to be shown on marketplaces.",
                        null=True,
                        verbose_name="attributes",
                    ),
                ),
                (
                    "properties",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="NFT properties to be shown on marketplaces.",
                        null=True,
                        verbose_name="properties",
                    ),
                ),
                (
                    "external_url",
                    models.URLField(
                        blank=True,
                        default=None,
                        help_text="External URL to be shown on marketplaces.",
                        max_length=4096,
                        null=True,
                        verbose_name="external url",
                    ),
                ),
                (
                    "redirect",
                    models.URLField(
                        blank=True,
                        default=None,
                        help_text=(
                            "URL to which an ISCC resolver should redirect for the registered"
                            " ISCC-ID."
                        ),
                        max_length=4096,
                        null=True,
                        verbose_name="redirect",
                    ),
                ),
                (
                    "original",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        help_text=(
                            "Whether the signee claims to be the original creator of the digital"
                            " content."
                        ),
                        null=True,
                        verbose_name="original",
                    ),
                ),
                (
                    "verifications",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text=(
                            "A list of self-verifications (Public URLs under the authority of the"
                            " signee."
                        ),
                        null=True,
                        verbose_name="verifications",
                    ),
                ),
                (
                    "result",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="The result returned by the NFT generator.",
                        null=True,
                        verbose_name="result",
                    ),
                ),
                (
                    "media_id_animation",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        help_text="ID of Media object to be used as NFT animation",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nft_animation",
                        to="iscc_generator.media",
                        verbose_name="media animation",
                    ),
                ),
                (
                    "media_id_image",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        help_text="ID of Media object to be used as NFT immage",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nft_image",
                        to="iscc_generator.media",
                        verbose_name="media image",
                    ),
                ),
            ],
            options={
                "verbose_name": "NFT",
            },
        ),
        migrations.CreateModel(
            name="IsccCode",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    models.PositiveBigIntegerField(
                        default=iscc_generator.base.make_flake,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "iscc",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default=None,
                        editable=False,
                        help_text="International Standard Content Code",
                        max_length=73,
                        null=True,
                        verbose_name="ISCC",
                    ),
                ),
                (
                    "source_url",
                    models.URLField(
                        blank=True,
                        default=None,
                        help_text="URL of file used for generating the ISCC-CODE",
                        max_length=4096,
                        null=True,
                        verbose_name="source_url",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text=(
                            "The title or name of the work manifested by the media asset. Used as"
                            " input for the ISCC Meta-Code"
                        ),
                        max_length=128,
                        null=True,
                        verbose_name="name",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default=None,
                        help_text=(
                            "Description of the digital content identified by the ISCC. Used as"
                            " input for the ISCC Meta-Code."
                        ),
                        max_length=4096,
                        null=True,
                        verbose_name="description",
                    ),
                ),
                (
                    "meta",
                    models.TextField(
                        blank=True,
                        default=None,
                        help_text=(
                            "Subject, industry, or use-case specific metadata, encoded as JSON"
                            " string or Data-URL (used as sole input for Meta-Code and `metahash`"
                            " generation if supplied)."
                        ),
                        max_length=16384,
                        null=True,
                        verbose_name="meta",
                    ),
                ),
                (
                    "creator",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text="An entity primarily responsible for making the resource.",
                        max_length=128,
                        null=True,
                        verbose_name="creator",
                    ),
                ),
                (
                    "license",
                    models.URLField(
                        blank=True,
                        default=None,
                        help_text="URL of license for the digital content.",
                        max_length=4096,
                        null=True,
                        verbose_name="license",
                    ),
                ),
                (
                    "acquire",
                    models.URLField(
                        blank=True,
                        default=None,
                        help_text="URL for acquiring a license for the digital content.",
                        max_length=4096,
                        null=True,
                        verbose_name="acquire",
                    ),
                ),
                (
                    "result",
                    models.JSONField(
                        blank=True,
                        default=None,
                        help_text="The result returned by the ISCC generator.",
                        null=True,
                        verbose_name="result",
                    ),
                ),
                (
                    "source_file",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        help_text="File used for ISCC-CODE creation",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="iscc_codes",
                        to="iscc_generator.media",
                        verbose_name="souce_file",
                    ),
                ),
            ],
            options={
                "verbose_name": "ISCC-CODE",
                "verbose_name_plural": "ISCC-CODES",
            },
        ),
    ]
