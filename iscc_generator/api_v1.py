# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional
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
        model_fields = ["name", "description"]


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
    response={200: IsccResponse, 202: TaskResponse, 503: Message},
    exclude_defaults=True,
    summary="Generate ISCC-CODE",
    tags=["iscc_code"],
)
def generate_iscc_code(
    request,
    source_file: Optional[UploadedFile] = File(None),
    meta: IsccRequest = Form(...),
):
    """
    ## Generate an ISCC for a media asset.

    Provide at least a `source_file` or optionally a `source_url`. If processing finishes fast
    you will receive an `IsccResponse`. If processing exeeds the time limit you will receive
    a `TaskResponse` instead to poll for the result at /task/{task_id}.
    """
    ico = IsccCode.objects.create(source_file=source_file, **meta.dict())
    task_id = async_task(create_iscc_code, ico.id)
    task_result = result(task_id, config.PROCESSING_TIMEOUT)
    if task_result:
        return 200, IsccCode.objects.get(id=ico.id)
    else:
        task = find_task(task_id)
        if not task:
            return 503, Message(message="Task not found")
        return 202, task


@router.get(
    "/task/{task_id}",
    response={200: TaskResponse, 404: Message},
    exclude_none=True,
    tags=["iscc_code"],
)
def get_task(request, task_id: str):
    task = find_task(task_id)
    if not task:
        return 404, Message(message="Task not found")
    return 200, task


def find_task(task_id):
    task = None
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        for queued in OrmQ.objects.all():
            if queued.task_id() == task_id:
                task = queued.task()
                break
    return task
