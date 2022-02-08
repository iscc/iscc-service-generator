# -*- coding: utf-8 -*-
from django.contrib.admin import AdminSite


class IsccAdminSite(AdminSite):

    site_url = "/api/docs"

    def get_app_list(self, request):
        """Customize admin app names and ordering"""
        applist = super().get_app_list(request)

        ordered = {
            "iscc_generator": "ISCC Generator",
            "django_q": "Background Tasks",
            "auth": "User Management",
            "constance": "Configuration",
            "admin_interface": "Branding",
        }

        new_applist = []
        for app_label, name in ordered.items():
            for app in applist:
                if app.get("app_label") == app_label:
                    app["name"] = name
                    new_applist.append(app)

        return new_applist
