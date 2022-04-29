import requests
from loguru import logger as log
from django.conf import settings
from eth_utils.address import to_checksum_address
from iscc_generator.codegen.spec import NftPostRequest
import iscc_core as ic


def normalize_web3_address(item: NftPostRequest) -> NftPostRequest:
    if item.chain in ("ETHEREUM", "POLYGON"):
        item.wallet = to_checksum_address(item.wallet)
    return item


def forecast_iscc_id(iscc_code: str, chain_id: str, wallet: str) -> str:
    iscc_code = ic.iscc_clean(iscc_code)
    chain_map = dict(PRIVATE=0, BITCOIN=1, ETHEREUM=2, POLYGON=3)
    if not isinstance(chain_id, str):
        raise ValueError("chain_id must be string")
    data = dict(
        iscc_code=iscc_code,
        chain_id=chain_map[chain_id],
        wallet=wallet,
    )
    if settings.ISCC_ID_FORECAST_URL:
        url = settings.ISCC_ID_FORECAST_URL
        try:
            resp = requests.post(url, json=data)
            iscc_id = resp.json()["iscc_id"]
        except Exception as e:
            log.warning("failed iscc-id remote forecasting, fallback to local")
            log.exception(e)
            iscc_id = ic.gen_iscc_id(**data)["iscc"]
    else:
        log.warning("no remote forecast url configured, using local forcasting")
        iscc_id = ic.gen_iscc_id(**data)["iscc"]
    return iscc_id
