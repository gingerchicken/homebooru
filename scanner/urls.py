from django.urls import path

from . import views

urlpatterns = [
    # Admin
    path('scan/<int:scanner_id>', views.scan, name='scan'),
]