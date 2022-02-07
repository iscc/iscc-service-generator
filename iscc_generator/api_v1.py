# -*- coding: utf-8 -*-
import time
from typing import Optional
from django_q.tasks import async_task, result
from django_q.models import Task
from ninja import Router, UploadedFile, File, Form, ModelSchema, Schema, Field

from iscc_generator.models import IsccCode
from iscc_generator.tasks import create_iscc_code
from constance import config


router = Router()


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


class TaskResponse(ModelSchema):
    class Config:
        model = Task
        model_fields = [
            "id",
            "started",
            "stopped",
            "success",
            "attempt_count",
        ]


@router.post(
    "/iscc_code",
    response={200: IsccResponse, 202: TaskResponse},
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
    """
    ico = IsccCode.objects.create(source_file=source_file, **meta.dict())
    djq_task_id = async_task(create_iscc_code, ico.id)
    task_result = result(djq_task_id, config.PROCESSING_TIMEOUT)
    if task_result:
        return IsccCode.objects.get(id=ico.id)
    task = None
    while not task:
        task = Task.get_task(djq_task_id)
        time.sleep(1)
    return 202, task
