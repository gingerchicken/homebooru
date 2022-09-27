import time

# Watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Django models
from django.db import models
from .scanner import Scanner

class ScannerWatcherHandler(FileSystemEventHandler):
    """Handles file system events for scanners"""

    def __init__(self, watchdog):
        self.watchdog = watchdog

    def run_scanner(self):
        # Get the scanner
        if self.watchdog.should_delete:
            return
        
        scanner = self.watchdog.scanner

        if scanner.is_active:
            # Do not run the scanner if it is already running
            return
        
        # Run the scanner
        scanner.scan()

    def on_any_event(self, event):
        if event.is_directory:
            return None
        
        # Check if it is a file change
        if event.event_type == 'modified':
            return self.run_scanner()
        
        # Check if it is a file creation
        if event.event_type == 'created':
            return self.run_scanner()

class ScannerObserver():
    """Watches a scanner for changes"""

    def __init__(self, watchdog):
        self.watchdog = watchdog

        # Create the observer
        self.observer = Observer()

        # Create the event handler
        self.event_handler = ScannerWatcherHandler(self.watchdog)

        # Start the observer
        self.observer.schedule(self.event_handler, self.watchdog.path, recursive=True)
        self.observer.start()

    def stop(self):
        """Stops the watcher"""
        self.observer.stop()
        self.observer.join()

class ScannerWatchDog(models.Model):
    """Stores the status of the watchdog"""

    is_running = models.BooleanField(default=False)

    # Path
    path = models.CharField(unique=True, max_length=512)

    @property
    def __scanners(self):
        """Returns the scanners that are watching this path"""
        return Scanner.objects.filter(path=self.path)

    @property
    def scanner(self):
        """Gets the scanner that is watching this path"""

        return self.__scanners.first()
    
    @property
    def should_delete(self):
        """Checks if the watchdog should be deleted"""

        return len(self.__scanners) == 0
    
    @staticmethod
    def prune():
        """Deletes all the watchdogs that should be deleted"""

        for watchdog in ScannerWatchDog.objects.all():
            if not watchdog.should_delete: continue

            watchdog.delete()
    
    def run(self):
        """Runs the watchdog"""

        # Check if the watchdog is already running
        if self.is_running: return

        # Set the running flag
        self.is_running = True
        self.save()

        # Create the observer
        observer = ScannerObserver(self)

        # Create a function that checks that the object still exists
        def check_exists():
            # Check if the watchdog still exists
            return len(ScannerWatchDog.objects.filter(id=self.id)) > 0

        # Wait for the path to change or the scanner to be deleted
        while check_exists() and not self.should_delete and self.path == self.scanner.path:
            time.sleep(5) # sleep for 5 seconds to avoid CPU usage
        
        # Stop the observer
        observer.stop()

        if not check_exists():
            # The watchdog was deleted
            return "Watchdog was deleted"
        
        # Delete the watchdog
        self.delete()

        return "Path changed or scanner was deleted"
    
    @staticmethod
    def from_scanner(scanner):
        """Creates a watchdog from a scanner"""

        # Check if the scanner already has a watchdog
        if len(ScannerWatchDog.objects.filter(path=scanner.path)) > 0:
            return
        
        # Create the watchdog
        watchdog = ScannerWatchDog(path=scanner.path)
        watchdog.save()