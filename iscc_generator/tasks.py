# -*- coding: utf-8 -*-
import os
from urllib.parse import urlparse
import requests
from blake3 import blake3
from django.conf import settings
import secrets
import iscc_sdk as idk


def create_iscc_code(pk: int):
    """
    Create an ISCC Code for an IsccCode database object.

    :param int pk: Primary key of the IsccCode entry
    :return: The result of the ISCC processor
    :rtype: dict
    """
    from iscc_generator.models import IsccCode

    obj = IsccCode.objects.get(pk=pk)

    # Download file if required
    if not obj.source_file and not obj.source_url:
        return {"error", "either source_file or source_url required"}
    elif obj.source_url and not obj.source_file:
        hashname = download_file(obj.source_url)
        filepath = os.path.join(settings.MEDIA_ROOT, hashname)
        # Set properties from downladed file
        # internal local file name
        obj.source_file.name = hashname
        # source filename
        url_obj = urlparse(obj.source_url)
        remote_name = os.path.basename(url_obj.path or url_obj.netloc)
        obj.source_file_name = remote_name
        # media type
        obj.source_file_mediatype = idk.mediatype_guess(open(filepath, 'wb').read(4096), remote_name)
        # file size
        obj.source_file_size = os.path.getsize(filepath)
    else:
        filepath = obj.source_file.path

    # Generate ISCC-CODE
    iscc_result = idk.code_iscc(
        filepath,
    )
    obj.iscc = iscc_result.iscc
    obj.result = iscc_result.dict()
    obj.save()
    return iscc_result


def download_file(url: str) -> str:
    """Download file and return local path"""
    filename = secrets.token_hex(64)
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    with open(filepath, "wb") as outfile:
        r = requests.get(url, stream=True)
        chunk_size = 1024 * 1024
        hasher = blake3()
        for chunk in r.iter_content(chunk_size):
            hasher.update(chunk)
            outfile.write(chunk)
    hashname = hasher.hexdigest()
    finalpath = os.path.join(settings.MEDIA_ROOT, hashname)
    os.rename(filepath, finalpath)
    return hashname
