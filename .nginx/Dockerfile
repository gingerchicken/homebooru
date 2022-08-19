FROM nginx

# Add the booru configuration file
COPY conf /etc/nginx/conf.d/booru.conf

# Add SSL configuration
COPY ssl/params.conf /etc/nginx/snippets/ssl-params.conf
COPY ssl/signed.conf /etc/nginx/snippets/ssl-signed.conf

# Add Security configuration
COPY sec/validate.conf /etc/nginx/snippets/sec-validate.conf
COPY sec/ratelimit.conf /etc/nginx/snippets/sec-ratelimit.conf
COPY sec/apply-ratelimit.conf /etc/nginx/snippets/sec-apply-ratelimit.conf

# Create the certs directory
RUN mkdir /certs/

# Self-signed certificate
RUN openssl req -new -newkey rsa:4096 -nodes -x509 -keyout /certs/booru.key -out /certs/booru.crt -days 365 -subj "/C=US/ST=California/L=San Francisco/O=Homebooru/OU=Homebooru/CN=booru.local"

# Create the pem file
RUN openssl dhparam -out /certs/dhparam.pem 4096