# -*- coding: utf-8 -*-
from ninja import NinjaAPI
from iscc_generator.api_v1 import router as generator_router
from iscc_service_generator import __version__


api = NinjaAPI(
    title="ISCC Generator",
    version=__version__,
    description="A webservice for generating ISCC codes",
)
api.add_router("/", generator_router, tags=["generate"])
