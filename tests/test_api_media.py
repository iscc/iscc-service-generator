import os

import iscc_samples as samples
import requests
from django.core.files.uploadedfile import SimpleUploadedFile


def test_media_post_empty(live_server):
    url = live_server.url + "/api/media"
    response = requests.post(url)
    assert response.status_code == 400
    assert response.json() == {"detail": "No file sent"}


def test_media_post_image(live_server):
    url = live_server.url + "/api/media"
    with samples.images("jpg")[0].open("rb") as file:
        response = requests.post(url, files={"source_file": file})
        assert response.status_code == 201
        assert "media_id" in response.json()


def test_media_post_unsupported(live_server, tmp_path):
    tf = tmp_path / "raw.bin"
    tf.write_bytes(os.urandom(1024))
    url = live_server.url + "/api/media"
    with tf.open("rb") as file:
        response = requests.post(url, files={"source_file": file})
        assert response.status_code == 500
        assert "detail" in response.json()


def test_media_get_none(live_server):
    url = live_server.url + "/api/media/05VN6J5C067J4"
    resp = requests.get(url)
    assert resp.status_code == 404


def test_media_get_image(live_server):
    url = live_server.url + "/api/media"
    with samples.images("jpg")[0].open("rb") as file:
        resp = requests.post(url, files={"source_file": file})
        media_id = resp.json().get("media_id")
    resp = requests.get(url + "/" + media_id)
    assert resp.headers["content-type"] == "image/jpeg"


def test_media_metadata(live_server):
    # upload asset
    url = live_server.url + "/api/media"
    with samples.images("jpg")[0].open("rb") as file:
        resp = requests.post(url, files={"source_file": file})
        media_id = resp.json().get("media_id")
    # get pre-existing metadata
    meta_endpoint = url + f"/metadata/{media_id}"
    resp = requests.get(meta_endpoint)
    assert resp.json() == {"creator": "Some Cat Lover", "name": "Concentrated Cat"}
    # embed new metadata
    meta = {
        "name": "new name",
        "description": "new description",
        "rights": "some copyright notice",
    }
    resp = requests.post(meta_endpoint, json=meta)
    new_media_id = resp.json().get("media_id")
    # get newly embedded metadata
    resp = requests.get(url + f"/metadata/{new_media_id}")
    assert resp.json() == {
        "creator": "Some Cat Lover",
        "description": "new description",
        "name": "new name",
        "rights": "some copyright notice",
    }
