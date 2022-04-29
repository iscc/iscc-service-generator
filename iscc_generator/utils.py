from eth_utils.address import to_checksum_address

from iscc_generator.codegen.spec import NftPostRequest


def normalize_web3_address(item: NftPostRequest) -> NftPostRequest:
    if item.chain in ("ETHEREUM", "POLYGON"):
        item.wallet = to_checksum_address(item.wallet)
    return item
