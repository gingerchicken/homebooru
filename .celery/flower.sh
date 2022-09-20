#!/bin/bash

# Check if we need to run unit tests
if [ "$UNIT_TEST" = "True" ]; then
    # Exit
    exit 0
fi

# Run the celery flower
worker_ready() {
    celery -A homebooru inspect ping
}

until worker_ready; do
  >&2 echo 'Celery workers not available'
  sleep 5
done
>&2 echo 'Celery workers is available'

celery -A homebooru --broker="redis://redis:6379" flower