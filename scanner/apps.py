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
        
        # Make sure that we should clean up the database
        CLEANUP_DATABASE = os.environ.get('CLEANUP_DATABASE', 'false').lower() == 'true'

        if not CLEANUP_DATABASE:
            return

        # Import the ScannerWatchdogs
        from .models import ScannerWatchDog

        # Delete them all
        print('Removing watchdogs')
        ScannerWatchDog.objects.all().delete()

        # Set all scanners as not running
        from .models import Scanner

        print('Setting all scanners as not running (inactive)')
        for scanner in Scanner.objects.all():
            scanner.is_active = False
            scanner.save()
