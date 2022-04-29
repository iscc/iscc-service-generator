# -*- coding: utf-8 -*-
from iscc_generator import utils
from iscc_generator.codegen.spec import NftPostRequest


def test_normalize_web3_address():
    item = NftPostRequest(
        media_id_image="05VJUVTH3DCP6",
        chain="ETHEREUM",
        wallet="0xb794f5ea0ba39494ce839613fffba74279579268",
    )
    norm = utils.normalize_web3_address(item)
    assert norm.wallet == "0xb794F5eA0ba39494cE839613fffBA74279579268"
