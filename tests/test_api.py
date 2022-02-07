# -*- coding: utf-8 -*-
import json
import pathlib
import sys
import iscc_service_generator

ROOT = pathlib.Path(sys.path[1]).absolute()
HERE = pathlib.Path(__file__).parent.absolute()

MEDIA = (
    HERE.parent.absolute() / ".scratch/media/admin-interface/logo/iscc-logo-blue-bg.png"
)


def test_project_version():
    assert iscc_service_generator.__version__ == "0.1.0"


def test_api_generate_iscc(client, live_server):
    url = live_server.url + "/api/iscc_code"
    with open(MEDIA, "rb") as infile:
        response = client.post(
            url,
            {
                "source_file": infile,
                "name": "Some title",
                "description": "Somedescription",
            },
        )

    assert json.loads(response.content) == {
        "description": "Somedescription",
        "filename": "iscc-logo-blue-bg.png",
        "iscc": "KEDQIPKHHOMBZZK32DAANP3ZJ6DHGEIAR3GWSEVO5LDC4UEDZ7FQPTA",
        "name": "Some title",
    }
