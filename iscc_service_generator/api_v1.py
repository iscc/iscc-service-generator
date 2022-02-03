# -*- coding: utf-8 -*-
from ninja import NinjaAPI
from iscc_generator.api_v1 import router as generator_router

api = NinjaAPI(
    title="ISCC Generator",
    version="1.0.0",
    description="A webservice for generating ISCC codes",
)
api.add_router("/", generator_router, tags=["generate"])
