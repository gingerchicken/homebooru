#!/bin/bash

# Create the database migrations
python manage.py makemigrations

# Migrate the database
python manage.py migrate --run-syncdb

# Start the application
python manage.py runserver 0.0.0.0:8000