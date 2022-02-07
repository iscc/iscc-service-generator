# -*- coding: utf-8 -*-
from typing import Optional

from django_q.tasks import async_task, result
from django_q.models import Task
from ninja import Router, UploadedFile, File, Form, ModelSchema
from pydantic import Field

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
            "result",
            "started",
            "stopped",
            "success",
            "attempt_count",
        ]


@router.post(
    "/iscc_code",
    response={200: IsccResponse, 202: TaskResponse},
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
    metadata = meta.dict()
    ico = IsccCode.objects.create(source_file=source_file, **metadata)
    djq_task_id = async_task(create_iscc_code, ico.id)
    task_result = result(djq_task_id, config.PROCESSING_TIMEOUT)
    if task_result:
        return 200, IsccCode.objects.get(id=ico.id)
    return 202, Task.objects.get(id=djq_task_id)
