import os
from celery import Celery

# I set this up as the same way as this documentation:
# https://realpython.com/asynchronous-tasks-with-django-and-celery/

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homebooru.settings')

app = Celery('homebooru')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()