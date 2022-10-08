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

# Copy the self-sign script
COPY self-sign.sh /certs/self-sign.sh

# Copy the start script
COPY start.sh /start.sh

# Make the scripts executable
RUN chmod +x /certs/self-sign.sh
RUN chmod +x /start.sh

# Environment variables
ENV SELF_SIGN=True

# Run the start script
CMD "/start.sh"