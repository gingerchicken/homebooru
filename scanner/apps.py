from django.apps import AppConfig

import os

class ScannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scanner'

    def ready(self):
        # Make sure unit tests don't run this since it's not needed
        # and if the database isn't set up yet, it will fail, where in the normal case it would be setup
        UNIT_TEST = os.environ.get('UNIT_TEST', 'false').lower() == 'true'
        
        if UNIT_TEST:
            return

        # Import the ScannerWatchdogs
        from .models import ScannerWatchDog

        # Delete them all
        ScannerWatchDog.objects.all().delete()