from django.db import models

from .scanner import Scanner

class ScannerStatus(models.Model):
    # Add a scanner field to the ScannerStatus model
    scanner = models.OneToOneField(Scanner, on_delete=models.CASCADE)

    # Add a field to the ScannerStatus model that stores the status of the scanner
    status = models.TextField(default='Idle')

    # Last time the status was updated
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.status