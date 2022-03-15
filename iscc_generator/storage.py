"""Storage related functions."""
from io import BytesIO
from os.path import basename, getsize, join
import tempfile
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
    media_obj.type, mode_ = idk.mediatype_and_mode(fp)
    media_obj.size = getsize(fp)
    if mode_ == "image":
        media_obj.metadata = idk.image_meta_extract(fp)
    elif mode_ == "audio":
        media_obj.metadata = idk.audio_meta_extract(fp)

    media_obj.cid = idk.ipfs_cidv1(fp)
    media_obj.original = original

    storage_name = f"{media_obj.flake}/{filename}"
    media_obj.source_file.name = storage_name
    storage: Storage = default_storage
    with open(fp, "rb") as infile:
        storage.save(storage_name, infile)
    media_obj.save()
    return media_obj


def store_local_temp(fileobj, filename):
    # type: (BytesIO, str) -> str
    """
    Store `fileobj` in local temp storage with `filename`.

    :param BytesIO fileobj: A readable object with cursor at start
    :param str filename: The name of the file
    :return: Filepath of localy stored file
    :rtype: str
    """
    tempdir = tempfile.mkdtemp()
    tmpfile_path = join(tempdir, clean_filename(filename))
    with open(tmpfile_path, "wb") as tmpfile:
        data = fileobj.read(1024 * 1024)
        while data:
            tmpfile.write(data)
            data = fileobj.read(1024 * 1024)
    return tmpfile_path
