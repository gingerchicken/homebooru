from django.apps import AppConfig


class ScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scanner'

    def ready(self):
        # Import the ScannerWatchdogs
        from .models import ScannerWatchDog

        # Delete them all
        ScannerWatchDog.objects.all().delete()