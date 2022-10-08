#!/bin/bash

# Check if we need to self-sign
if [ "$SELF_SIGN" = "True" ]; then
    echo "Self-signing certificate..."
    ./certs/self-sign.sh
fi

# Run the nginx server
nginx -g "daemon off;"