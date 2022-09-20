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