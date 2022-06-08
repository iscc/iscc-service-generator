# -*- coding: utf-8 -*-
import iscc_samples as samples
import requests


def test_nft_post_empty(live_server):
    url = live_server.url + "/api/nft"
    reponse = requests.post(url, json={})
    assert reponse.status_code == 422
    assert reponse.json() == {
        "detail": [
            {
                "loc": ["body", "item", "media_id_image"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


def test_nft_post_invalid_media_id_image(live_server):
    url = live_server.url + "/api/nft"
    reponse = requests.post(url, json={"media_id_image": "badid"})
    assert reponse.status_code == 422
    assert reponse.json() == {
        "detail": [
            {
                "ctx": {"limit_value": 13},
                "loc": ["body", "item", "media_id_image"],
                "msg": "ensure this value has at least 13 characters",
                "type": "value_error.any_str.min_length",
            }
        ]
    }


def test_nft_post_missing_media_id_image(live_server):
    url = live_server.url + "/api/nft"
    reponse = requests.post(url, json={"media_id_image": "05VJUVTH3DCP6"})
    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Not found."}


def test_nft_post_with_media_upload(live_server):
    url = live_server.url + "/api/media"
    with samples.images("jpg")[0].open("rb") as file:
        response = requests.post(url, files={"source_file": file})
        media_id = response.json().get("media_id")
    url = live_server.url + "/api/nft"
    reponse = requests.post(url, json={"media_id_image": media_id})
    assert reponse.status_code == 201
    result = reponse.json()
    del result["nft_id"]
    del result["nft_image"]
    del result["nft_metadata"]["media_id"]
    assert result == {
        "iscc_code": "ISCC:KECWRY3VY6R5SNV4YNBTBHR4T2HGP3HKVFO7TYUP2BKVFG724W63HVI",
        "nft_metadata": {
            "$schema": "http://purl.org/iscc/schema/0.3.8.json",
            "@context": "http://purl.org/iscc/context/0.3.8.jsonld",
            "@type": "ImageObject",
            "creator": "Some Cat Lover",
            "datahash": "1e2055529bfae5bdb3d530c52f44d13ccd6a7c710f63620dc2db1c43c5592ae2dc97",
            "filename": "demo.jpg",
            "filesize": 35393,
            "height": 133,
            "image": "ipfs://bafkreibpvnkawhupqto4zouc3nve5rjyahddf33agrksajkdos3q2ud4iq",
            "iscc": "ISCC:KECWRY3VY6R5SNV4YNBTBHR4T2HGP3HKVFO7TYUP2BKVFG724W63HVI",
            "mediatype": "image/jpeg",
            "metahash": "1e209ce5052a03004657d8657167f53812718e9426d85b4cdd5106ef3d87412e6f64",
            "mode": "image",
            "name": "Concentrated Cat",
            "thumbnail": "data:image/webp;base64,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",
            "width": 200,
        },
    }


def test_nft_post_with_animation_url(live_server):
    url = live_server.url + "/api/media"
    with samples.images("jpg")[0].open("rb") as file:
        response = requests.post(url, files={"source_file": file})
        media_id_image = response.json().get("media_id")
    with samples.images("png")[0].open("rb") as file:
        response = requests.post(url, files={"source_file": file})
        media_id_animation = response.json().get("media_id")

    url = live_server.url + "/api/nft"
    reponse = requests.post(
        url,
        json={
            "media_id_image": media_id_image,
            "media_id_animation": media_id_animation,
        },
    )

    assert reponse.status_code == 201
    result = reponse.json()
    del result["nft_id"]
    del result["nft_image"]
    del result["nft_metadata"]["media_id"]
    assert result == {
        "iscc_code": "ISCC:KECSR5352MR7TNV4YNBTBHR4T2HGO6RDNMJX4P6UMT7LQXYXBH2R5PY",
        "nft_metadata": {
            "$schema": "http://purl.org/iscc/schema/0.3.8.json",
            "@context": "http://purl.org/iscc/context/0.3.8.jsonld",
            "@type": "ImageObject",
            "animation_url": "ipfs://bafkreicl4rhrzfmuqfcn7nvyd32nto4uba2swwy332zgqkpyweppk3zdpm",
            "creator": "Another Cat Lover",
            "datahash": "1e20feb85f1709f51ebf31c2feab2092a61826da36cc79eddc4cb04800b47db146a6",
            "filename": "demo.png",
            "filesize": 54595,
            "height": 133,
            "image": "ipfs://bafkreibpvnkawhupqto4zouc3nve5rjyahddf33agrksajkdos3q2ud4iq",
            "iscc": "ISCC:KECSR5352MR7TNV4YNBTBHR4T2HGO6RDNMJX4P6UMT7LQXYXBH2R5PY",
            "mediatype": "image/png",
            "metahash": "1e2011dfae49dd718631175cbb05a9c459d19a25556ff3c03692bc3a5fc87c623740",
            "mode": "image",
            "name": "Concentrated Cat PNG",
            "thumbnail": "data:image/webp;base64,UklGRgoIAABXRUJQVlA4IP4HAAAQJwCdASqAAFUAPrVKnUsnJCKhrhkqYOAWiWdMAFuK9fc4UQbLfaNtOLt9oFBWreZrHlO+tPYO3Xhs3WPC5xbScRS8aZ7yt15nm//EXQcSDnfz5uRWBHQzu5g4mzyp2/crYlm31vN6f5gVWS/OqwbieT/Swyk4VThbW8s0Nd9riA4le9varDcGMRSa0CcGppHm5fuzrO+QN88nD3OBE4VPBljSwaxClZ0MmSukdOjAK149SXHr0JauUEMHEcZHVnsaBDmP4dmv2d6xPlAF08TKGh7uPYsH2tMRfocj+FcUtz9n68cbDN9+NYKE37GgHuayhXTGyckEipP+Zzk0Q2tG4r0HvG0mVaGq4yTLw+YXU2AN7Xy4y9bQaM9LJlKsTPAk3Jazi0UkcEaDPDwLD0FjPQo9yfR5lWMQLJNwIAsuIZIA/vvHcyZlZDqjO4ldOVgH3oQeVVY4u+tFWzO+4cw99U+7m8+e9MNhfhyrNEDzjPz83mGL1TMw+rTDULEihP79ECXMWWYFYn2z7VghIoy8dAzFuZCr0CWoroJZw9XiJ8OWtZ4PMQAELY1kn2KW5ZXZKDwPt0YOqn1/JgpfP8BQPxn3KjA444IOWDkDVdO7vZjn6vJl23evfN0iQwMrW7mwiR9Zvq1QXOmDToLHmC9c1FXG9i7l+JXJBTYCDW3BY9KE4E+xaJNGVWN0/eeOMTxENnkqp3rOabnaOpkKOESYylCbdVdoQEwJN8A3ZPMOoZTRuR5r9RTpZkx+l811cPdFIwhnmpIPJzfITwSW3PX6WSTFjVyJfAx/ZOj62jk7lmga7SUhKq6u8HCtJaiL40CvGZPu7ZEv/vZvhLI2myPL+huc4+KgENNoBzZ+Ev2qKgwn8aJN+sZ1CjZkCYHz/6GbQyi6UbaHrPgrIEXlQMc/e1xHT9LFgVaOtSvQd4wPsIDcDrTdP5kYEvFvl/DvTqMa7L3QxMtlOm8Jmk0moFIsiXUHzbQVqOveeTuY+/tW0r3lcrVZRKf/6UXOEGfGpGjLd+td42j6UNtDDxbIttlH+xvfjgFVdX5xYtMmBgZCV/N8+R6mg3a7v5oUO105x+8py+He+6YHZKfjVxsEqK9YiXIsuom6tj7bzJbdbNdvc5VEEu/740ph76+Ar8JfYa0ea2fs4tSb+vP8DTg7ymrCbmok+dMVICTyvro9wJSvBaDVz2XaRtTKWZWXQzX7qzhgC24lSBhzOjQJj561E/e693v68++cj353AB7/7wBMhlsSA1uyY8kWSjBReKKqxzsElg07PgDUvcA/MRv+403LQSikT8YZnTWRknB5mts3LY3Q/Xs9dBhjBgrV8KpFeYXQa1LE79qVD4n3zq4IOj49fn7GtkBYPBWGby8HMQ5eyg9PXim39ADdimD7nqe2ToUq/xXuzRz/zE2jx0enbZnr6CMlHzOifU0IIJReM1oDITf/XFX2fMcOPWL607kEty9UIU/ky7H+aqV/c374fVDTeaBL+jHqSRbHt9i+MpkiVX9WY8zCyHhHayMAUSxvmbSFuBgzcO4ACJLJx5dk9hNgwSxyqpB0YhERWVn8dNU6G0uq2/fR1xuCn4keAA+9jyzxVSE18bP863QVcvePObhzDOnOPb4eGTe4ijGi813wdDGmYtfzU2/G66gy7C30ohr8UYLcXeNsWunBVa+LfqLplxW3XIg/k8J04MeO8L1LoPMYiwFf9Gs0FOyRChyqNmzK/bMF6SFqEoxqtWqow+uPPZT4euPbI5jL48T1QVEEbjLMLcZHK5wLIqumrU+avEBX4Lsk29Ttfuw59U6bumW4v49ZXjn/nv0hkeB1jXWspTLi7q8bjhrO9CGWOj/z7IHoZM7vid5jAiAh3Wgte2J5qsptBsfLz1nfk+YGWtXMKOMBqvNIcHBscDebncNwkkHkUDPiifbQVlOPJyQhuqClpOaH7D7oJpw63dJxEHILS6+jkiGfEwZl1541mUlJd9w04XIiMMgJyubiBwBO+5EkOK3Zf8somftbpfqpEk6Z5SN4e4GqP1/iM54lxISPfBz13qjSvahVmAhrFWWs2FZ+KDGhnJz9Txx+xcC07JT8io76AJCXGdES3C46kRJ6qVcrjYpV1O9uJfwNuIr37iLCn5h1CqR+HTaUHA7gMQiBXJ4bePg9aw7n2k8l2mwZQxoz36lR+tLYjVtploO4PaJ82eqs5Hp+8xr73Rn37j4trKU4PzZLeUQQ0kkkGMjc4t29aWfDnVn9aBH4S9I+BIFDs4HkzgquYcG+PicJQVL2A0X/JtnANvDg0ZhngHcZ/T24KwlmvQ40EtcesQ57Bjpu3qIzxDOTKoZDtevO8U9dTBrNVAWpv8WDz/Px6dLG2Znf3EFBGOJV/v8LlHxUOVZ25AMIn8c1aa2BLKqQ+6GSwcOj5Ay+R97VTHvUFmC99+RDVz1Q+m2+bmSClfxM2Zifv+G0L94xkeX1GLXOhGB7iZfCZjvUbxVQkWFX6keU8QoPC0V4abGeaIpRKW/Bxgg0+PvohxN0w0P/lJTGE1w61rjQpGrz6mIHjblq62RcEM8QtpVAxzx5ov4yd+Y6+9uI2YAEx0XiBO6iR1I+/+AfFvjOtZKuneXymk0+WjdJ6blnk9QsnAET1NsPYhTvxH/sSJj6Wm/8a8Py0Z23Pygn7RQNNygf48mfWzhGc4sZb+sIX8sFaa54A48Ud1b6rqE4MC37KWrwGpj5eSHIAAA=",
            "width": 200,
        },
    }
