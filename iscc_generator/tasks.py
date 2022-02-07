# -*- coding: utf-8 -*-
import iscc


def create_iscc_code(task_id):
    from iscc_generator.models import IsccCode

    iscc_code_obj = IsccCode.objects.get(id=task_id)
    iscc_result = iscc.code_iscc(
        iscc_code_obj.source_file.path,
        title=iscc_code_obj.name,
        extra=iscc_code_obj.description,
    )
    iscc_code_obj.iscc = iscc_result["iscc"]
    iscc_code_obj.result = iscc_result
    iscc_code_obj.save()
    return iscc_result
