# -*- coding: utf-8 -*-
import base64
import io
import json
from datetime import datetime
from os.path import join, basename
from tempfile import TemporaryDirectory
from typing import Optional
from asgiref.sync import sync_to_async
from data_url import DataURL
from django.shortcuts import redirect
from django_q.tasks import async_task, result
from django_q.models import Task, OrmQ
from iscc_schema.generator import (
    MediaID,
    MediaEmbeddedMetadata,
    NftPackage,
    NftFrozen,
)
from ninja import Router, File, Form, ModelSchema, Schema, UploadedFile
from iscc_generator.base import get_or_404
from iscc_generator.models import IsccCode, Media, Nft
from iscc_generator.schema import AnyObject, NftRequest, IsccMeta
from iscc_generator.storage import media_obj_from_path
from iscc_generator.tasks import iscc_generator_task, nft_generator_task
from constance import config
import iscc_sdk as idk
import iscc_core as ic


router = Router()


class Message(Schema):
    detail: str


class IsccRequest(ModelSchema):
    class Config:
        model = IsccCode
        model_fields = ["source_url", "name", "description", "meta"]


class TaskResponse(Schema):
    id: str
    name: str
    started: datetime
    stopped: Optional[datetime]
    success: Optional[bool]
    attempt_count: Optional[int]
    result: Optional[dict]


@router.post(
    "/iscc_code",
    response={201: IsccMeta, 202: TaskResponse, 400: Message, 500: Message},
    summary="create iscc",
    tags=["iscc"],
    operation_id="iscc-code-create",
    exclude_none=True,
    by_alias=True,
)
async def iscc_code_create(
    request,
    source_file: Optional[UploadedFile] = File(
        None, description="The file used for generating the ISCC"
    ),
    meta: IsccRequest = Form(...),
):
    """
    ## Generate an ISCC for a media asset.

    Provide at least a `source_file` or optionally a `source_url`. If processing finishes fast
    you will receive an `IsccResponse`. If processing exeeds the configured time limit you will
    receive a `TaskResponse` to poll for the result at /task/{task_id}.

    Metadata supplied with the file upload will be embedded into the media asset (if possible).
    You can download the modified media asset based on the `vendor_id` field of the returned
    ISCC Metadata with a GET request to /media/<vendor_id>.
    """
    # validate the request
    if not source_file and not meta.source_url:
        return 400, Message(detail="Either source_file or source_url is required")
    if meta.meta:
        if meta.meta.startswith("data:"):
            try:
                DataURL.from_url(meta.meta)
            except Exception:
                return 500, Message(detail="Invalid Data-URL in field meta")
        else:
            try:
                json.loads(meta.meta)
            except Exception:
                return 500, Message(detail="Invalid JSON-string in field meta")

    media_obj = None
    # Create Media object if source_file provided (source_url will be handled by worker task).
    if source_file:
        try:
            media_obj = await sync_to_async(Media.objects.create)(
                source_file=source_file
            )
        except Exception as e:
            return 500, Message(detail=str(e))

    # create IsccCode object
    iscc_obj = await sync_to_async(IsccCode.objects.create)(
        source_file=media_obj, **meta.dict()
    )

    # start processing
    task_id = await sync_to_async(async_task)(iscc_generator_task, iscc_obj.pk)

    # wait for result with timeout
    task_result = await async_wait_for_task(task_id)
    if task_result:
        iscc_obj = await sync_to_async(IsccCode.objects.get)(pk=iscc_obj.pk)
        return 201, iscc_obj.result
    # return task-id instead
    else:
        task = await async_find_task(task_id)
        if not task:
            return 503, Message(detail="Task not found")
        return 202, task


@router.get(
    "/iscc_code/{iscc}",
    response={200: IsccMeta, 404: Message},
    exclude_defaults=False,
    exclude_unset=True,
    summary="get iscc",
    tags=["iscc"],
    operation_id="iscc-code-get",
)
async def iscc_code_get(request, iscc: str):
    """
    Get metadata for previously generated ISCC-CODE
    """
    try:
        iscc = ic.iscc_normalize(iscc)
        objs = await sync_to_async(list)(IsccCode.objects.filter(iscc=iscc))
        return objs[0].result
    except Exception:
        return 404, Message(detail="ISCC-CODE not found")


@router.delete(
    "/iscc_code/{iscc}",
    response={200: Message, 404: Message},
    summary="delete iscc",
    tags=["iscc"],
    operation_id="iscc-code-delete",
)
async def iscc_code_delete(request, iscc: str):
    """
    Delete ISCC-CODE entry from database.
    """
    try:
        iscc = ic.iscc_normalize(iscc)
        iscc_code_obj: IsccCode = await sync_to_async(IsccCode.objects.get)(iscc=iscc)
        await sync_to_async(iscc_code_obj.delete)()
        return 200, Message(detail="ISCC-CODE deleted")
    except Exception:
        return 404, Message(detail="ISCC-CODE not found")


####################################################################################################
# /media endpoints                                                                                 #
####################################################################################################


@router.post(
    "/media",
    tags=["media"],
    operation_id="post-media",
    response={201: MediaID, 400: Message, 500: Message},
    summary="upload media",
)
async def media_post(request, source_file: UploadedFile = File(None)):
    """Upload Media."""
    if not source_file:
        return 400, Message(detail="No file sent")

    try:
        media_obj = await sync_to_async(Media.objects.create)(source_file=source_file)
    except Exception as e:
        return 500, Message(detail=e.__class__.__name__)
    return 201, MediaID(media_id=media_obj.flake)


@router.get(
    "/media/{media_id}",
    tags=["media"],
    operation_id="get-media",
    summary="download media",
)
async def media_get(request, media_id):
    media_obj: Media = await get_or_404(Media, media_id)
    return redirect(media_obj.source_file.url)


@router.delete(
    "/media/{media_id}",
    tags=["media"],
    operation_id="delete-media",
    response={200: Message, 404: None},
    summary="delete media",
)
async def media_delete(request, media_id: str):
    """Delete media asset"""
    media_obj: Media = await get_or_404(Media, media_id)
    await sync_to_async(media_obj.delete)()

    return 200, Message(detail="Media asset deleted")


@router.post(
    "media/metadata/{media_id}",
    tags=["media"],
    operation_id="embed-metadata",
    response={201: MediaID, 400: Message},
    summary="embed metadata",
)
async def media_metadata_embed(request, media_id: str, meta: MediaEmbeddedMetadata):
    """Embeds metadata into media asset and returns `media_id` of new asset."""
    if not meta.dict(exclude_none=True):
        return 400, Message(detail="No embeddable metadata provided")

    media_obj: Media = await get_or_404(Media, media_id)
    new_media_obj = await async_media_metadata_embed(media_obj, meta)
    return 201, MediaID(media_id=new_media_obj.flake)


@sync_to_async
def async_media_metadata_embed(media_obj: Media, meta: MediaEmbeddedMetadata):
    """
    Embed metadata into a media file.

    # TODO - we need to download/reupload the file - move this to a worker task
    """
    meta = IsccMeta.parse_obj(meta.dict())
    # Copy file to local storage
    filename = basename(media_obj.source_file.name)
    with TemporaryDirectory() as tempdir:
        tmpfile_path = join(tempdir, filename)
        with open(tmpfile_path, "wb") as tmpfile:
            with media_obj.source_file.open("rb") as infile:
                data = infile.read(1024 * 1024)
                while data:
                    tmpfile.write(data)
                    data = infile.read(1024 * 1024)
        # Embed metadata
        idk.image_meta_embed(tmpfile_path, meta=meta)
        # Create new media object
        new_media_object = media_obj_from_path(tmpfile_path, original=media_obj)

    return new_media_object


@router.get(
    "media/metadata/{media_id}",
    tags=["media"],
    operation_id="get-media-metadata",
    response={200: MediaEmbeddedMetadata, 400: None, 404: None},
    exclude_none=True,
    summary="extract metadata",
)
async def media_metadata_get(request, media_id: str):
    """Reads and returns embedded metadata from the media asset."""
    media_obj: Media = await get_or_404(Media, media_id)
    return media_obj.metadata


####################################################################################################
# /nft endpoints                                                                                   #
####################################################################################################


@router.post(
    "/nft",
    tags=["nft"],
    operation_id="post-nft",
    summary="create nft",
    response={201: NftPackage, 400: Message, 404: Message, 500: Message},
    exclude_unset=True,
)
async def nft_post(request, item: NftRequest):
    """Creates an NFT package"""
    if not item.iscc_code:
        return 400, Message(detail="missing required field 'iscc_code'")
    try:
        ic.iscc_validate(item.iscc_code, strict=True)
    except Exception as e:
        return 400, Message(detail=f"{item.iscc_code} is an invalid ISCC-CODE - {e}")
    try:
        iscc_obj = await sync_to_async(IsccCode.objects.get)(iscc=item.iscc_code)
    except IsccCode.DoesNotExist:
        return 404, Message(detail=f"{item.iscc_code} does not exist")
    item = item.dict()
    item["iscc_code"] = iscc_obj
    nft_obj = await sync_to_async(Nft.objects.create)(**item)

    # start processing
    task_id = await sync_to_async(async_task)(nft_generator_task, nft_obj.pk)

    # wait for result with timeout
    task_result = await async_wait_for_task(task_id)
    if task_result:
        await sync_to_async(nft_obj.refresh_from_db)()
        return 201, nft_obj.result
    # return task-id instead
    else:
        task = await async_find_task(task_id)
        if not task:
            return 503, Message(detail="Task not found")
        return 202, task


@router.get(
    "/nft/{nft_id}",
    tags=["nft"],
    operation_id="get-nft",
    summary="get nft",
    response={200: NftPackage, 404: Message},
    exclude_none=True,
)
async def nft_get(request, nft_id: str):
    nft_obj: Nft = await get_or_404(Nft, nft_id)
    return nft_obj.result


@router.delete(
    "/nft/{nft_id}",
    tags=["nft"],
    operation_id="delete-nft",
    response={200: Message, 404: None},
    summary="delete nft",
)
async def nft_delete(request, nft_id: str):
    nft_obj: Nft = await get_or_404(Nft, nft_id)
    await sync_to_async(nft_obj.delete)()

    return 200, Message(detail="Media asset deleted")


@router.post(
    "/nft/freeze",
    tags=["nft"],
    operation_id="post-nft-freeze",
    summary="freeze nft",
    response={200: NftFrozen, 400: Message},
    exclude_none=True,
)
async def nft_freeze_post(request, anyobject: AnyObject):
    """
    Creates a Token-ID and IPFS CIDv1 for NFT metadata.

    Post the contents of the `nft_metadata` field from the `/nft` entpoint to this endpoint if you
    want to mint your NFT with a Token-ID that is derived from the IPFS CIDv1 of the nft metadata.

    NFT-Freezing will use deterministic JCS serialization (RFC8785) to create the IPFS payload.
    The payload is than used to create the Token-ID and IPFS CIDv1 URI (base16). The deterministic
    payload is also returned (base64 encoded) for publishing to IPFS after the NFT has been minted.
    """
    data = anyobject.dict().get("__root__")
    if not data:
        return 400, Message(detail="No JSON data provided")

    canonical = ic.json_canonical(data)
    cid = ic.cidv1_hex(io.BytesIO(canonical))
    token_id_num = ic.cidv1_to_token_id(cid)
    return NftFrozen(
        token_id_hex=cid.lstrip("f01551220"),
        token_id_num=str(token_id_num),
        metadata_ipfs_uri=f"ipfs://{cid}",
        metadata_ipfs_payload=base64.b64encode(canonical).decode("ascii"),
    )


####################################################################################################
# /task endpoints                                                                                  #
####################################################################################################


@router.get(
    "/task/{task_id}",
    response={200: TaskResponse, 404: Message},
    exclude_none=True,
    tags=["task"],
    operation_id="get-task",
)
async def get_task(request, task_id: str):
    task = await async_find_task(task_id)
    if not task:
        return 404, Message(detail="Task not found")
    return 200, task


####################################################################################################
# Sync to Async functions                                                                          #
####################################################################################################


@sync_to_async
def async_create_generator_task(iscc_pk) -> str:
    return async_task(iscc_generator_task, iscc_pk)


@sync_to_async
def async_wait_for_task(task_id):
    return result(task_id, config.PROCESSING_TIMEOUT * 1000)


@sync_to_async
def async_find_task(task_id):
    task = None
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        for queued in OrmQ.objects.all():
            if queued.task_id() == task_id:
                task = queued.task()
                break
    return task


@sync_to_async
def async_get_iscc_code(pk: Optional[int] = None, iscc: Optional[str] = None):
    try:
        if pk:
            return IsccCode.objects.get(pk=pk)
        elif iscc:
            return IsccCode.objects.get(iscc=iscc)
    except IsccCode.DoesNotExist:
        return None
