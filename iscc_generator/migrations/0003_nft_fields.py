# Generated by Django 4.0.4 on 2022-04-29 16:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("iscc_generator", "0002_theme"),
    ]

    operations = [
        migrations.AddField(
            model_name="nft",
            name="nft_chain",
            field=models.CharField(
                blank=True,
                choices=[
                    ("PRIVATE", "Private"),
                    ("BITCOIN", "Bitcoin"),
                    ("ETHEREUM", "Ethereum"),
                    ("POLYGON", "Polygon"),
                ],
                default=None,
                help_text="Blockchain that hosts the NFT for the digital content.",
                max_length=32,
                null=True,
                verbose_name="nft_chain",
            ),
        ),
        migrations.AddField(
            model_name="nft",
            name="nft_contract",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="Smartcontract address of the NFT for the digital content.",
                max_length=128,
                null=True,
                verbose_name="nft_contract",
            ),
        ),
        migrations.AddField(
            model_name="nft",
            name="nft_token",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="Token-ID of the NFT for the digital content (as string).",
                max_length=255,
                null=True,
                verbose_name="nft_token",
            ),
        ),
    ]
