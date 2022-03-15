# -*- coding: utf-8 -*-
import json

import requests


def test_nft_post_empty(live_server):
    url = live_server.url + "/api/nft"
    reponse = requests.post(url, json={})
    assert reponse.status_code == 400
    assert reponse.json() == {"detail": "missing required field 'iscc_code'"}


def test_nft_post_invalid_iscc_code(live_server):
    url = live_server.url + "/api/nft"
    reponse = requests.post(url, json={"iscc_code": "ISCC:LOOKALIKE"})
    assert reponse.status_code == 400
    assert reponse.json() == {
        "detail": "ISCC:LOOKALIKE is an invalid ISCC-CODE - "
        "ISCC string does not match ^ISCC:[A-Z2-7]{10,60}$"
    }


def test_nft_post_invalid_iscc_code_missing(live_server):
    url = live_server.url + "/api/nft"
    data = json.dumps(
        {"iscc_code": "ISCC:KMD5MO6ZVATK7EOBJY2ED5CVIEZ4IW2ATWZ6SX2VQLROZORS5W5TR6A"}
    )
    reponse = requests.post(url, data=data)
    assert reponse.status_code == 404
    assert reponse.json() == {
        "detail": "ISCC:KMD5MO6ZVATK7EOBJY2ED5CVIEZ4IW2ATWZ6SX2VQLROZORS5W5TR6A does not exist"
    }
