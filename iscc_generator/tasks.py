# -*- coding: utf-8 -*-
import json

from data_url import DataURL
from loguru import logger as log
import os
import iscc_sdk as idk
import iscc_core as ic
from iscc_schema import IsccMeta
from iscc_generator.download import download_media, download_url
from iscc_generator.storage import media_obj_from_path


def iscc_generator_task(pk: int):
    """
    Create an ISCC Code for an IsccCode database object.

    - retrieves asset to local temp storage
    - embeds metadata
    - stores new Media object
    - generates ISCC
    - stores result in IsccCode
    - removes temp file

    :param int pk: Primary key of the IsccCode entry
    :return: The result of the ISCC processor
    :rtype: dict
    """
    from iscc_generator.models import IsccCode

    iscc_obj = IsccCode.objects.get(pk=pk)

    # ensure meta is a data url
    if iscc_obj.meta and not iscc_obj.meta.startswith("data:"):
        data = json.loads(iscc_obj.meta)
        serialized = ic.json_canonical(data)
        durl_obj = DataURL.from_data(
            "application/json", base64_encode=True, data=serialized
        )
        meta_durl = durl_obj.url
    else:
        meta_durl = iscc_obj.meta

    meta_obj = IsccMeta()
    meta_obj.name = iscc_obj.name or None
    meta_obj.description = iscc_obj.description or None
    meta_obj.meta = meta_durl or None

    media_obj = iscc_obj.source_file

    # retrieve file
    if media_obj:
        temp_fp = download_media(media_obj)
    elif iscc_obj.source_url:
        temp_fp = download_url(iscc_obj.source_url)
    else:
        raise ValueError("No source_file and not source_url.")

    # embed metadata
    if meta_obj.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True):
        mt, mode_ = idk.mediatype_and_mode(temp_fp)
        if mode_ == "image":
            idk.image_meta_embed(temp_fp, meta_obj)
        elif mode_ == "audio":
            idk.audio_meta_embed(temp_fp, meta_obj)
        else:
            return dict(details=f"Unsupported mode {mode_} for mediatype {mt}")

    # remote store and set new media object
    new_media_obj = media_obj_from_path(temp_fp, original=media_obj)
    iscc_obj.source_file = new_media_obj
    iscc_obj.save()

    # generate iscc code
    iscc_result = idk.code_iscc(temp_fp)
    iscc_obj.iscc = iscc_result.iscc
    iscc_obj.result = iscc_result.dict(exclude_defaults=False)
    iscc_obj.save()

    # cleanup
    try:
        os.remove(temp_fp)
    except OSError:
        log.warning(f"could not remove temp file {temp_fp}")

    return dict(result=iscc_result.iscc)


# def embed_metadata(media_id: int, meta: dict) -> str:
#     """Embed metadata into a copy of the media object"""
#
#     from django.core.files.storage import Storage
#
#     # Get database object
#     media_obj = Media.objects.get(media_id=media_id)
#     meta = IsccMeta.parse_obj(meta)
#
#     # Copy file to local storage
#     with TemporaryDirectory() as tempdir:
#         tmpfile_path = Path(tempdir) / media_obj.source_file.name
#         with tmpfile_path.open("wb") as tmpfile:
#             with media_obj.source_file.open("rb") as infile:
#                 data = infile.read(1024 * 1024)
#                 while data:
#                     tmpfile.write(data)
#                     data = infile.read(1024 * 1024)
#         # Embed metadata
#         idk.image_meta_embed(tmpfile_path, meta=meta)
#
#         # Create new media object with updated file
#         # new_media_obj = Media.objects.create()
#         # name = f"{new_media_obj.flake}/{media_obj.name}"
#
#         with tmpfile_path.open("rb") as tmpfile:
#             new_media_obj = Media.objects.create(source_file=tmpfile)
#     return new_media_obj.flake
