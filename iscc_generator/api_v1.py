# -*- coding: utf-8 -*-
from typing import Optional
from ninja import Router, UploadedFile, File, Schema, Form, ModelSchema
from pydantic import Field, Json
from iscc_generator.models import IsccTask, Media
from ninja.errors import HttpError


router = Router()


class IsccTaskRequest(Schema):
    source_url: Optional[str]
    name: Optional[str]
    description: Optional[str]
    metadata: Optional[Json] = Field({})


class IsccTaskRespone(ModelSchema):
    class Config:
        model = IsccTask
        model_exclude = ("source_file", "metadata")


@router.post("/iscc_code", response=IsccTaskRespone, summary="Generate ISCC-CODE")
def generate_iscc_code(
    request,
    source_file: Optional[UploadedFile] = File(None),
    meta: IsccTaskRequest = Form(...),
):
    """Generate an ISCC from a file upload or URL."""
    if source_file:
        media_obj = Media.objects.create(name=source_file.name, file=source_file)
        task_obj = IsccTask.objects.create(
            source_file=media_obj, metadata=meta.dict(exclude={"source_url"})
        )
    elif meta.source_url:
        task_obj = IsccTask.objects.create(
            source_url=meta.source_url, metadata=meta.dict()
        )
    else:
        raise HttpError(400, "Bad Request - either source_file or source_url required")
    return task_obj
