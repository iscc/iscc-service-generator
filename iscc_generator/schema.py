from typing import Dict, Optional
from pydantic import BaseModel
from ninja import ModelSchema
from iscc_generator.models import Nft


class AnyObject(BaseModel):
    """Any JSON mapping object"""

    __root__: Dict


class NftRequest(ModelSchema):

    iscc_code: Optional[str] = None

    class Config:
        model = Nft
        model_fields = [
            "iscc_code",
            "chain",
            "wallet",
            "attributes",
            "external_url",
            "redirect",
            "original",
            "verifications",
        ]


class NftSchema(ModelSchema):
    class Config:
        model = Nft
        model_fields = [
            "attributes",
            "external_url",
            "redirect",
            "original",
            "verifications",
        ]
