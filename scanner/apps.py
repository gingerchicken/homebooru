from django.apps import AppConfig

import homebooru.settings

class ScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scanner'

    def ready(self):
        # Make sure debug mode is disabled
        if homebooru.settings.DEBUG:
            return

        # Import the ScannerWatchdogs
        from .models import ScannerWatchDog

        # Delete them all
        ScannerWatchDog.objects.all().delete()