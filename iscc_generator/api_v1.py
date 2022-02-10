# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
from asgiref.sync import sync_to_async
from django_q.tasks import async_task, result
from django_q.models import Task, OrmQ
from ninja import Router, UploadedFile, File, Form, ModelSchema, Schema, Field
from iscc_generator.models import IsccCode
from iscc_generator.tasks import create_iscc_code
from constance import config


router = Router()


class Message(Schema):
    message: str


class IsccRequest(ModelSchema):
    class Config:
        model = IsccCode
        model_fields = ["source_url", "name", "description"]


class IsccResponse(ModelSchema):

    filename: Optional[str] = Field(
        ...,
        alias="source_file_name",
        description="Filename of the source used to create the ISCC",
    )

    class Config:
        model = IsccCode
        model_fields = ["iscc", "name", "description"]


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
    summary="Generate ISCC-CODE",
    tags=["iscc_code"],
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
        return 400, Message(message="either source_file or source_url is required")

    ico = await async_create_iscc_code(source_file, meta)
    task_id = await async_create_task(ico.pk)
    task_result = await async_wait_for_task(task_id)
    if task_result:
        obj = await async_get_iscc_code(ico.pk)
        return 200, obj
    else:
        task = await async_find_task(task_id)
        if not task:
            return 503, Message(message="Task not found")
        return 202, task


@router.get(
    "/task/{task_id}",
    response={200: TaskResponse, 404: Message},
    exclude_none=True,
    tags=["iscc_code"],
)
async def get_task(request, task_id: str):
    task = await async_find_task(task_id)
    if not task:
        return 404, Message(message="Task not found")
    return 200, task


####################################################################################################
# Sync to Async functions                                                                          #
####################################################################################################


@sync_to_async
def async_create_iscc_code(source_file, meta):
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
def async_get_iscc_code(pk):
    return IsccCode.objects.get(pk=pk)
