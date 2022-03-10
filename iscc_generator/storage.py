"""Storage related functions."""
from os.path import basename, getsize

import translitcodec
from django.core.files.storage import Storage, default_storage
from pathvalidate import sanitize_filename
import iscc_sdk as idk


def get_storage_path(instance, filename) -> str:
    """Create storage path with object-id as folder plus the sanitized filename"""
    filename = clean_filename(filename)
    return f"{instance.flake}/{filename}"


def clean_filename(filename: str) -> str:
    """Transliterate and sanitize filename"""
    filename, _ = translitcodec.long_encode(filename)
    return sanitize_filename(filename)


def media_obj_from_path(fp: str, original=None):
    """Create a media object from a filepath."""
    from iscc_generator.models import Media

    media_obj = Media.objects.create()
    filename = basename(fp)
    media_obj.name = filename
    media_obj.type, _ = idk.mediatype_and_mode(fp)
    media_obj.size = getsize(fp)
    media_obj.metadata = idk.image_meta_extract(fp)
    media_obj.original = original
    storage_name = f"{media_obj.flake}/{filename}"
    media_obj.source_file.name = storage_name
    storage: Storage = default_storage
    with open(fp, "rb") as infile:
        storage.save(storage_name, infile)
    media_obj.save()
    return media_obj
