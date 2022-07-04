from typing import Dict
from pydantic import BaseModel
from ninja import ModelSchema, Schema
from iscc_generator.models import Nft
from iscc_generator.codegen.spec import NftPackage as BaseNftPackage
import iscc_schema as iss


class AnyObject(BaseModel):
    """Any JSON mapping object"""

    __root__: Dict


class NftPackage(BaseNftPackage):
    nft_metadata: iss.IsccMeta


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
            "nft",
        ]


class QueuedTasks(Schema):
    """Number of tasks in the task queue."""

    queued_tasks: int
