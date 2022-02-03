# -*- coding: utf-8 -*-
import iscc


def create_iscc_code(task_id):
    from iscc_generator.models import IsccTask, IsccCode

    task_obj = IsccTask.objects.get(id=task_id)
    iscc_result = iscc.code_iscc(
        task_obj.source_file.file.path,
        title=task_obj.metadata.get("name"),
        extra=task_obj.metadata.get("description"),
    )
    IsccCode.objects.create(
        iscc=iscc_result["iscc"],
        name=iscc_result.get("title"),
        description=iscc_result.get("description"),
        metadata=iscc_result.get("metadata"),
    )
    return iscc_result
