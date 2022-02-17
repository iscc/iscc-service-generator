# Generated by Django 4.0.2 on 2022-02-17 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("iscc_generator", "0002_iscccode_embed_iscccode_metadata"),
    ]

    operations = [
        migrations.AlterField(
            model_name="iscccode",
            name="result",
            field=models.JSONField(
                blank=True,
                default=None,
                help_text="The result returned by the ISCC generator",
                null=True,
                verbose_name="result",
            ),
        ),
        migrations.AlterField(
            model_name="iscccode",
            name="source_file_mediatype",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                help_text="Original IANA Media Type (MIME type) from upload (autoset / untrusted)",
                max_length=255,
                verbose_name="mediatype",
            ),
        ),
        migrations.AlterField(
            model_name="iscccode",
            name="source_file_name",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                help_text="Original filename from upload (autoset / untrusted)",
                max_length=255,
                verbose_name="filename",
            ),
        ),
        migrations.AlterField(
            model_name="iscccode",
            name="source_file_size",
            field=models.PositiveBigIntegerField(
                default=0,
                editable=False,
                help_text="The filesize of the media asset",
                null=True,
                verbose_name="filesize",
            ),
        ),
        migrations.AlterField(
            model_name="iscccode",
            name="source_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text="URL of file used for generating the ISCC",
                max_length=4096,
                verbose_name="source_url",
            ),
        ),
    ]
