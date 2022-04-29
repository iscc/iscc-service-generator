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


def test_forecast_iscc_id_local():
    code = "ISCC:KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI"
    chain = "BITCOIN"
    wallet = "1Bq568oLhi5HvdgC6rcBSGmu4G3FeAntCz"
    iid = utils.forecast_iscc_id(code, chain, wallet)
    assert iid == "ISCC:MEAJU5AXCPOIOYFL"


def test_forecast_iscc_id_remote(use_forecast_url):
    code = "ISCC:KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI"
    chain = "ETHEREUM"
    wallet = "0xa2fFD293145d89D61b39a2842F35a52E89a317f5"
    iid = utils.forecast_iscc_id(code, chain, wallet)
    assert iid == "ISCC:MIAOPGRMQNJDQ6KO"
