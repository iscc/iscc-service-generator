from django.apps import AppConfig


class IsccGeneratorConfig(AppConfig):
    name = "iscc_generator"
    verbose_name = "ISCC Generator"

    def ready(self):
        from django.conf import settings

        if settings.SENTRY_DSN:
            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration

            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[DjangoIntegration()],
                send_default_pii=False,
            )
