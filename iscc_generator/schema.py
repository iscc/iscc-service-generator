from typing import Dict, Optional
from pydantic import BaseModel, Field
from ninja import ModelSchema
from iscc_generator.models import Nft
from iscc_sdk import IsccMeta as BaseIsccMeta


class IsccMeta(BaseIsccMeta):
    """
    Adds vendor_id field.

    TODO: add to iscc-schema and remove this patch.
    """

    vendor_id: Optional[str] = Field(
        None,
        description="Vendor specific internal identifier for media file.",
    )

    # mode: Optional[str] = Field(
    #     None,
    #     description="The perceptual mode used to create the ISCC-CODE",
    # )


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
