#!/bin/bash

# Create the database migrations
python manage.py makemigrations

# Migrate the database
python manage.py migrate --run-syncdb

# Check for the unit test enviroment variable
# If it is set and equal to "True" then run the unit tests
if [ "$UNIT_TEST" = "True" ]; then
    python manage.py test

    # Exit with the unit test exit code
    exit $?
fi

# Start the application
python manage.py runserver 0.0.0.0:8000