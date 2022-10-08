#!/bin/bash

cert() {
    # Generate a self-signed certificate with a key
    openssl req -new -newkey rsa:4096 -nodes -x509 -keyout /certs/booru.key -out /certs/booru.crt -days 365 -subj "/C=US/ST=California/L=San Francisco/O=Homebooru/OU=Homebooru/CN=booru.local"
}

dhparam() {
    # Generate the dhparam file
    openssl dhparam -out /certs/dhparam.pem 4096
}

# Check if the certificate exists
if [ ! -f /certs/booru.crt ]; then
    # Generate the certificate
    cert
fi

# Check if the dhparam exists
if [ ! -f /certs/dhparam.pem ]; then
    # Generate the dhparam
    dhparam
fi