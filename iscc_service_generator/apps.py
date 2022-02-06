# -*- coding: utf-8 -*-
from django.contrib.admin.apps import AdminConfig


class GeneratorAdminConfig(AdminConfig):
    default_site = "iscc_service_generator.admin.IsccAdminSite"
