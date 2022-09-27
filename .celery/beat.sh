#!/bin/bash

# Check if we need to run unit tests
if [ "$UNIT_TEST" = "True" ]; then
    # Exit
    exit 0
fi

# Run the celery beat
rm -f './celerybeat.pid'
celery -A homebooru beat -l INFO