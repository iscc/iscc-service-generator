# -*- coding: utf-8 -*-
from django.core.files.uploadhandler import FileUploadHandler
from django.conf import settings
from ninja.errors import HttpError
import humanize


class IsccUploadHandler(FileUploadHandler):
    """
    This upload handler terminates the connection if more than FILE_SIZE_LIMIT is uploaded.
    """

    def __init__(self, request=None):
        super().__init__(request)
        self.total_upload = 0
        self.quota = settings.UPLOAD_SIZE_LIMIT * 1000000

    def receive_data_chunk(self, raw_data, start):
        self.total_upload += len(raw_data)
        if self.total_upload >= self.quota:
            raise HttpError(
                400,
                message=f"Upload file size limit of {humanize.naturalsize(self.quota)} exeeded!",
            )
        return raw_data

    def file_complete(self, file_size):
        return None
