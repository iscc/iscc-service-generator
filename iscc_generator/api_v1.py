# -*- coding: utf-8 -*-
import json
from datetime import datetime
from json import JSONDecodeError
from os.path import join, basename
from tempfile import TemporaryDirectory
from typing import Optional

import iscc_sdk
from asgiref.sync import sync_to_async
from django.shortcuts import redirect
from django_q.tasks import async_task, result
from django_q.models import Task, OrmQ
from iscc_schema import IsccMeta
from iscc_schema.generator import MediaID, MediaEmbeddedMetadata
from ninja import Router, File, Form, ModelSchema, Schema, Field, UploadedFile
from loguru import logger as log
from iscc_generator.base import get_or_404
from iscc_generator.models import IsccCode, Media
from iscc_generator.storage import clean_filename, media_obj_from_path
from iscc_generator.tasks import create_iscc_code
from constance import config
import iscc_sdk as idk


router = Router()


class Message(Schema):
    detail: str


class IsccRequest(ModelSchema):
    class Config:
        model = IsccCode
        model_fields = ["source_url", "name", "description", "metadata"]


class IsccResponse(ModelSchema):

    filename: Optional[str] = Field(
        None,
        alias="source_file_name",
        description="Filename of the source used to create the ISCC",
    )

    class Config:
        model = IsccCode
        model_fields = ["iscc", "name", "description", "metadata"]


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
    response={200: IsccResponse, 202: TaskResponse, 400: Message, 503: Message},
    exclude_defaults=True,
    summary="Create ISCC-CODE",
    tags=["iscc_code"],
    operation_id="create-iscc-code",
)
async def generate_iscc_code(
    request,
    source_file: Optional[UploadedFile] = File(
        None, description="The file used for generating the ISCC"
    ),
    meta: IsccRequest = Form(...),
):
    """
    ## Generate an ISCC for a media asset.

    Provide at least a `source_file` or optionally a `source_url`. If processing finishes in time
    you will receive an `IsccResponse`. If processing exeeds the time limit you will receive
    a `TaskResponse` to poll for the result at /task/{task_id}.
    """

    if not source_file and not meta.source_url:
        return 400, Message(detail="either source_file or source_url is required")

    ico = await async_create_iscc_code(source_file, meta)
    task_id = await async_create_task(ico.pk)
    task_result = await async_wait_for_task(task_id)
    if task_result:
        obj = await async_get_iscc_code(pk=ico.pk)
        return 200, obj
    else:
        task = await async_find_task(task_id)
        if not task:
            return 503, Message(detail="Task not found")
        return 202, task


@router.get(
    "/iscc_code/{iscc}",
    response={200: IsccResponse, 404: Message},
    exclude_defaults=False,
    exclude_none=True,
    exclude_unset=True,
    summary="Get ISCC-CODE",
    tags=["iscc_code"],
    operation_id="get-iscc-code",
)
async def get_iscc_code(request, iscc: str):
    """
    Returns metadata for previously generated ISCC-CODE
    """
    iscc_code_obj = await async_get_iscc_code(iscc=iscc)
    if iscc_code_obj:
        return iscc_code_obj
    else:
        return 404, Message(detail="ISCC not found")


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
        media_obj = await async_media_post(source_file)
    except Exception as e:
        return 500, Message(detail=e.__class__.__name__)
    return 201, MediaID(media_id=media_obj.flake)


@sync_to_async
def async_media_post(source_file):
    return Media.objects.create(source_file=source_file)


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
    await async_media_delete(media_obj)

    return 200, Message(detail="Media asset deleted")


@sync_to_async
def async_media_delete(media_obj):
    media_obj.source_file.delete()
    media_obj.delete()


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
# Sync to Async functions                                                                          #
####################################################################################################


@sync_to_async
def async_create_iscc_code(source_file, meta: IsccRequest):

    # Decode json metadata
    try:
        meta.metadata = json.loads(meta.metadata)
    except JSONDecodeError:
        log.warning(f"failed to decode metadata {meta.metadata}")
        metadata = None
    #
    if source_file:
        return IsccCode.objects.create(source_file=source_file, **meta.dict())
    else:
        return IsccCode.objects.create(**meta.dict())


@sync_to_async
def async_create_task(iscc_pk) -> str:
    return async_task(create_iscc_code, iscc_pk)


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
