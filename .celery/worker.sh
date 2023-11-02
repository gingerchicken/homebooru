#!/bin/bash

# Check if we need to run unit tests
if [ "$UNIT_TEST" = "True" ]; then
    # Exit
    exit 0
fi

export IS_WORKER=True

# Run the celery worker
celery -A homebooru worker -l INFO -c $CELERY_WORKERS