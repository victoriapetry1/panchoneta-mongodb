from django.apps import AppConfig


class PanchonetaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'panchoneta'

    def ready(self):
        import panchoneta.signals