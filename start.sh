#!/bin/bash

# Check if we need to install jQuery
if [ "$INSTALL_JQUERY" = "True" ]; then
    # Feel free to check for more recent versions of jQuery: https://jquery.com/download/
    
    echo "Installing jQuery..."

    # Where to save the file
    JQUERY_PATH="./booru/static/js/thirdparty/jquery.min.js"

    # Download jQuery v3.6.0
    wget -O $JQUERY_PATH "https://code.jquery.com/jquery-3.6.0.min.js"

    # Check if the file was downloaded
    if [ ! -f $JQUERY_PATH ]; then
        echo "Error: jQuery was not downloaded."
        exit 1
    fi

    echo "jQuery installed to $JQUERY_PATH"
fi

# Check if the SECRET_KEY environment variable is set
if [ -z "$SECRET_KEY" ]; then
    # Check if ./secret.txt doesn't exist
    # or if ROLL_SECRET is set to True
    if [ ! -f ./secret.txt ] || [ "$ROLL_SECRET" = "True" ]; then
        # Generate a new secret
        python manage.py createsecretkey --force --length 128 > /dev/null
    fi

    # Read the secret from ./secret.txt
    SECRET=$(cat ./secret.txt)

    # Set it as an environment variable
    export SECRET_KEY=$SECRET

    echo "Pulled secret key from file"
else
    # Say that the secret is set
    echo "Pulled secret from environment variable"
fi

if [ "$DB_MIGRATE" = "True" ]; then
    # Migrate booru
    python manage.py makemigrations booru
    python manage.py migrate

    # Migrate scanner
    python manage.py makemigrations scanner
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
    coverage run --omit=*/tests/*.py,*/migrations/*.py --source=./booru,./scanner manage.py test --verbosity 2

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
    # Enable the static file app
    export COLLECT_STATIC=True

    # Collect static files
    python manage.py collectstatic --noinput --clear | grep "static files" # This grep just prints out how many files were collected
    
    # Disable
    export COLLECT_STATIC=False
fi

# Start the application
if [ "$DEBUG" = "True" ]; then
    if [ "$CREATE_ROOT" = "True" ]; then
        echo 'Creating root user for debugging...'

        # Create the root user
        python manage.py createrootuser
    fi

    export CELERY_RUN_TASKS=True
    # Start the application in debug mode
    python manage.py runserver 0.0.0.0:8000
else
    export CELERY_RUN_TASKS=True
    # Start the application in production mode
    gunicorn homebooru.wsgi:application -b 0.0.0.0:8000 --workers $WORKERS
fi