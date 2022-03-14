# -*- coding: utf-8 -*-
import requests


def test_iscc_code_post_empty(live_server):
    url = live_server.url + "/api/iscc_code"
    response = requests.post(url)
    assert response.status_code == 400
    assert response.json() == {"detail": "Either source_file or source_url is required"}
