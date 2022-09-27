from django.db import models

class ScannerIgnore(models.Model):
    # The checksum to ignore (MD5)
    md5 = models.CharField(unique=True, blank=False, null=False, max_length=32)

    # The reason for ignoring the checksum
    reason = models.TextField(blank=True, null=False)

    # Date and time the checksum was ignored
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.md5 + " - " + self.reason