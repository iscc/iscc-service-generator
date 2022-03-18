from typing import Dict, Optional
from pydantic import BaseModel, Field
from ninja import ModelSchema, Schema
from iscc_generator.models import Nft
from iscc_sdk import IsccMeta as BaseIsccMeta
from iscc_generator.codegen.spec import NftPackage as BaseNftPackage


class IsccMeta(BaseIsccMeta):
    """
    Adds vendor_id field.

    TODO: add to iscc-schema and remove this patch.
    """

    media_id: Optional[str] = Field(
        None,
        description="Vendor specific internal identifier for media file.",
    )

    class Config(BaseIsccMeta.Config):
        orm_mode = True


class AnyObject(BaseModel):
    """Any JSON mapping object"""

    __root__: Dict


class NftPackage(BaseNftPackage):

    nft_metadata: Dict


class NftSchema(ModelSchema):
    class Config:
        model = Nft
        model_fields = [
            "chain",
            "wallet",
            "attributes",
            "properties",
            "external_url",
            "redirect",
            "original",
            "verifications",
        ]


class QueuedTasks(Schema):
    """Number of tasks in the task queue."""

    queued_tasks: int
