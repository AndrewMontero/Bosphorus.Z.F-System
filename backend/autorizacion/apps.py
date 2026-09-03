from django.apps import AppConfig


class AutorizacionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "autorizacion"
    verbose_name = "Autorización"

    def ready(self):
        from . import signals  # noqa: F401
