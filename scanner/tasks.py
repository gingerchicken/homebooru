from celery import shared_task

# Logger
import logging
logger = logging.getLogger(__name__)

from scanner.models import Scanner
    
@shared_task
def scan_all():
    # Get all the scanners
    scanners = Scanner.objects.all()

    # Trigger a scan event for each scanner
    for scanner in scanners:
        scan.delay(scanner.id)

@shared_task
def scan(scanner_id):
    # Get the scanner
    scanner = Scanner.objects.get(id=scanner_id)

    # Make sure that it is not active
    if scanner.is_active: return

    # Run the scan function
    results = scanner.scan()

    # Return the results' ids
    return [result.id for result in results]

from .models.watchdog import ScannerWatchDog

@shared_task
def register_watchdog(scanner_id):
    # Get the scanner
    scanner = Scanner.objects.get(id=scanner_id)

    # Get all the watchdogs with the same path
    watchdogs = ScannerWatchDog.objects.filter(path=scanner.path)

    # Check if there is already a watchdog for this path
    if len(watchdogs) > 0:
        return "Watchdog already exists for this path."
    
    # Create the watchdog
    watchdog = ScannerWatchDog(path=scanner.path)

    # Save the watchdog
    watchdog.save()

    # Run the watchdog
    return watchdog.run()


@shared_task
def register_all_watchdogs():
    """Registers all scanners with the watchdog"""

    # Prune the watchdogs
    ScannerWatchDog.prune()

    # Get all the scanners
    scanners = Scanner.objects.all()

    total_watchdogs = 0

    # Register each scanner
    for scanner in scanners:
        # Get all the watchdogs with the same path
        watchdogs = ScannerWatchDog.objects.filter(path=scanner.path)

        # Check if there is already a watchdog for this path
        if len(watchdogs) > 0:
            continue

        # If not, register the watchdog
        register_watchdog.delay(scanner.id)

        total_watchdogs += 1

    return f"Registered {total_watchdogs} watchdogs."