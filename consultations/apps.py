from django.apps import AppConfig


class ConsultationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'consultations'
    verbose_name = 'Обращения и консультации'

    def ready(self):
        from . import signals  # noqa: F401
