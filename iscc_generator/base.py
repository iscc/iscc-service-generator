"""Model base class."""
from asgiref.sync import sync_to_async
from loguru import logger as log

from django.db import models
from django.contrib import admin
from model_utils.models import TimeStampedModel
import iscc_core as ic
from ninja.errors import HttpError


def make_flake() -> int:
    """Create flake-id."""
    return ic.Flake().int


class Flake(ic.Flake):
    """Flake with additional creation methods."""

    @classmethod
    def from_int(cls, num):
        # type: (int) -> Flake
        """Instantiate  flake from integer."""
        flake_obj = Flake()
        flake_obj._flake = num.to_bytes(8, "big", signed=False)
        flake_obj._bits = 64
        return flake_obj

    @classmethod
    def from_string(cls, code):
        """Instantiate flake from string."""
        raw = ic.decode_base32hex(code)
        flake_obj = Flake()
        flake_obj._flake = raw
        flake_obj._bits = 64
        return flake_obj


class GeneratorBaseModel(TimeStampedModel):
    """Base class with flake-id and created/modified"""

    class Meta:
        abstract = True

    id = models.PositiveBigIntegerField(
        primary_key=True, editable=False, default=make_flake
    )

    @property
    @admin.display(ordering="id", description="ID")
    def flake(self):
        return Flake.from_int(self.id).string


@sync_to_async
def get_or_404(model: models.Model, flake: str):
    """Get object by flake-id."""

    try:
        pk = Flake.from_string(flake)
        obj = model.objects.get(pk=pk)
    except Exception as e:
        log.error(e)
        raise HttpError(404, "Not found.")

    return obj
