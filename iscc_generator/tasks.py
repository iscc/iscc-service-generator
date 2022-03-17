# -*- coding: utf-8 -*-
import json
from data_url import DataURL
from loguru import logger as log
import os
import iscc_sdk as idk
import iscc_core as ic
from iscc_generator.download import download_media, download_url
from iscc_generator.models import Nft
from iscc_generator.schema import NftSchema, IsccMeta
from iscc_generator.storage import media_obj_from_path
from constance import config


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
    # Updgrade to customized
    iscc_result = IsccMeta.parse_obj(iscc_result.dict())
    # Set vendor_id
    iscc_result.vendor_id = new_media_obj.flake

    iscc_obj.iscc = iscc_result.iscc
    iscc_obj.result = iscc_result.dict()
    iscc_obj.save()

    # cleanup
    try:
        os.remove(temp_fp)
    except OSError:
        log.warning(f"could not remove temp file {temp_fp}")

    return dict(result=iscc_result.iscc)


def nft_generator_task(pk: int):
    """
    Create an NftPackage for an IsccCode database object.

    :param int pk: Primary key of the Nft entry
    :return: The result of the NFT processor
    :rtype: dict
    """

    # Patch standard ISCC Metadata with NFT metadata
    nft_obj = Nft.objects.get(pk=pk)
    nft_patch = NftSchema.from_orm(nft_obj).dict(
        exclude_unset=True, exclude_none=True, exclude_defaults=True
    )
    iscc_meta = nft_obj.iscc_code.result
    iscc_meta.update(nft_patch)

    # Set ISCC-ID if chain and wallet are provided
    chain_map = dict(PRIVATE=0, BITCOIN=1, ETHEREUM=2, POLYGON=3)
    iscc_code = iscc_meta["iscc"]
    if nft_obj.chain and nft_obj.wallet:
        iscc_id = ic.gen_iscc_id(
            iscc_code=iscc_meta.iscc,
            chain_id=chain_map[nft_obj.chain],
            wallet=nft_obj.wallet,
        )
        iscc_meta["iscc"] = iscc_id["iscc"]

    # Set NFT image IPFS hash
    iscc_meta["image"] = f"ipfs://{nft_obj.iscc_code.source_file.cid}"

    # Wrap in NFTPackage
    np = dict(
        nft_id=nft_obj.flake,
        iscc_code=iscc_code,
        nft_metadata=iscc_meta,
        nft_image=f"{config.DOMAIN}{nft_obj.iscc_code.source_file.source_file.url}",
    )
    nft_obj.result = np
    nft_obj.save()
    return dict(result=nft_obj.flake)
