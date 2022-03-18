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
    media_obj = iscc_obj.source_file

    # retrieve file for local processing
    if media_obj:
        temp_fp = download_media(media_obj)
    elif iscc_obj.source_url:
        temp_fp = download_url(iscc_obj.source_url)
    else:
        raise ValueError("No source_file and not source_url.")

    # embed user provided metadata
    user_metadata = iscc_obj.get_metadata()
    if user_metadata.dict(exclude_unset=True):
        # ensure IsccMeta.meta is a data url for embedding
        if iscc_obj.meta and not iscc_obj.meta.startswith("data:"):
            data = json.loads(iscc_obj.meta)
            serialized = ic.json_canonical(data)
            durl_obj = DataURL.from_data(
                "application/json", base64_encode=True, data=serialized
            )
            user_metadata.meta = durl_obj.url
        else:
            user_metadata.meta = iscc_obj.meta

        mt, mode_ = idk.mediatype_and_mode(temp_fp)
        if mode_ == "image":
            idk.image_meta_embed(temp_fp, user_metadata)
        elif mode_ == "audio":
            idk.audio_meta_embed(temp_fp, user_metadata)
        else:
            return dict(details=f"Unsupported mode {mode_} for mediatype {mt}")

        # remote store and set new media object
        media_obj = media_obj_from_path(temp_fp, original=media_obj)
        iscc_obj.source_file = media_obj
        iscc_obj.save()

    # generate iscc code
    iscc_result_obj = idk.code_iscc(temp_fp)
    # iscc_result_data = iscc_result_obj.dict(by_alias=True, exclude_none=True, exclude_unset=False)
    # # Updgrade to customized
    iscc_result = IsccMeta.parse_obj(iscc_result_obj.dict())
    # Set media_id
    iscc_result.media_id = media_obj.flake

    iscc_obj.iscc = iscc_result_obj.iscc
    iscc_obj.result = iscc_result.dict(
        by_alias=True, exclude_none=True, exclude_unset=False
    )
    iscc_obj.save()

    # local file cleanup
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
    nft_obj = Nft.objects.get(pk=pk)

    # Choose the Media object
    media_obj = (
        nft_obj.media_id_animation
        if nft_obj.media_id_animation
        else nft_obj.media_id_image
    )

    # Get or create IsccCode
    if media_obj.iscc_codes.exists():
        iscc_obj = media_obj.iscc_codes.first()
    else:
        # Create ISCC-CODE
        from iscc_generator.models import IsccCode

        iscc_obj = IsccCode.objects.create(source_file=media_obj)
        iscc_generator_task(iscc_obj.pk)
        iscc_obj.refresh_from_db()

    # Patch standard ISCC Metadata with NFT metadata
    nft_patch = NftSchema.from_orm(nft_obj).dict(
        exclude_unset=True, exclude_none=True, exclude_defaults=True
    )
    iscc_meta = iscc_obj.result
    iscc_meta.update(nft_patch)

    # Set ISCC-ID if chain and wallet are provided
    chain_map = dict(PRIVATE=0, BITCOIN=1, ETHEREUM=2, POLYGON=3)
    iscc_code = iscc_meta["iscc"]
    if nft_obj.chain and nft_obj.wallet:
        iscc_id = ic.gen_iscc_id(
            iscc_code=iscc_meta["iscc"],
            chain_id=chain_map[nft_obj.chain],
            wallet=nft_obj.wallet,
        )
        iscc_meta["iscc"] = iscc_id["iscc"]

    # Set NFT IPFS hashes
    iscc_meta["image"] = f"ipfs://{nft_obj.media_id_image.cid}"
    if nft_obj.media_id_animation:
        iscc_meta["animation_url"] = f"ipfs://{nft_obj.media_id_animation.cid}"

    # Wrap in NFTPackage
    np = dict(
        nft_id=nft_obj.flake,
        iscc_code=iscc_code,
        nft_metadata=iscc_meta,
        nft_image=f"{config.DOMAIN}{media_obj.source_file.url}",
    )
    nft_obj.result = np
    nft_obj.save()
    return dict(result=nft_obj.flake)
