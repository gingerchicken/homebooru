from django.db import models

class ScannerIgnore(models.Model):
    # The checksum to ignore (MD5)
    checksum = models.CharField(unique=True, blank=False, null=False, max_length=32)

    def __str__(self):
        return self.checksum