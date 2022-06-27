#!/bin/bash

if [ "$DB_MIGRATE" = "True" ]; then
    # Migrate booru
    python manage.py makemigrations booru
    python manage.py migrate

    # Migrate the rest of the site
    python manage.py makemigrations
    python manage.py migrate --run-syncdb
fi

# Check for the unit test enviroment variable
# If it is set and equal to "True" then run the unit tests
if [ "$UNIT_TEST" = "True" ]; then
    # Make sure that we extract the test data (assets/TEST_DATA.tar.gz into assets/TEST_DATA)
    if [ ! -d "assets/TEST_DATA" ]; then
        tar -xzf assets/TEST_DATA.tar.gz -C assets
    fi

    # Run the unit tests
    coverage run --omit=*/tests/*.py,*/migrations/*.py --source='./booru' manage.py test

    # Save the exit code of the unit tests
    UNIT_TEST_EXIT_CODE=$?

    # Check if we should display the report
    if [ "$UNIT_TEST_DISPLAY_COVERAGE" = "True" ]; then
        # Display the coverage report
        coverage report -m
    fi

    # Exit with the unit test exit code
    exit $UNIT_TEST_EXIT_CODE
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