# -*- coding: utf-8 -*-
from django.core.files.uploadedfile import SimpleUploadedFile
import iscc_service_generator
from ninja.testing import TestClient
from iscc_generator.api_v1 import router


client = TestClient(router)


def test_project_version():
    assert iscc_service_generator.__version__ == "0.1.0"


def test_api_generate_iscc_file_only(live_server):
    file = SimpleUploadedFile("test.txt", b"data123")
    response = client.post("/iscc_code", FILES={"source_file": file})
    assert response.status_code == 200
    assert response.json() == {
        "filename": "test.txt",
        "iscc": "KADR7VAIQA6XMAJYVUHPKVEVRHUQVLIO6VKJLCPJBL2UWXKVOGJZJBQ",
    }


def test_api_generate_iscc(live_server):
    file = SimpleUploadedFile("test.txt", b"data123")
    response = client.post(
        "/iscc_code",
        data={"name": "Some title", "description": "Other Description"},
        FILES={"source_file": file},
    )
    assert response.json() == {
        "description": "Other Description",
        "filename": "test.txt",
        "iscc": "KADQIPKHHONBZYD7VUHPKVEVRHUQVLIO6VKJLCPJBL2UWXKVOGJZJBQ",
        "name": "Some title",
    }
