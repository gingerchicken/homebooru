#!/bin/bash

# Create the database migrations
python manage.py makemigrations

# Migrate the database
python manage.py migrate --run-syncdb

# Check for the unit test enviroment variable
# If it is set and equal to "True" then run the unit tests
if [ "$UNIT_TEST" = "True" ]; then
    # Make sure that we extract the test data (assets/TEST_DATA.tar.gz into assets/TEST_DATA)
    if [ ! -d "assets/TEST_DATA" ]; then
        tar -xzf assets/TEST_DATA.tar.gz -C assets
    fi

    # Run the unit tests
    coverage run --source='./booru' manage.py test

    # Show the coverage report
    coverage report -m

    # Exit with the unit test exit code
    exit $?
fi

# Chcek if the LOAD_FIXTURES variable is set and equal to "True"
if [ "$LOAD_FIXTURES" = "True" ]; then
    # Load the fixtures
    python manage.py loaddata booru/fixtures/*.json
fi

# Check if the debug enviroment variable is set and equal to "False"
if [ "$DEBUG" = "False" ]; then
    # Collect static files
    echo "yes" | python manage.py collectstatic
fi

# Start the application
python manage.py runserver 0.0.0.0:8000