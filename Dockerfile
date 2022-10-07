FROM python:3

# Enviroment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Make the current working dir /app
WORKDIR /app

# Install ffmpeg
RUN apt update
RUN apt install -y ffmpeg

# Install magiclib
RUN apt install -y libmagic1

# Install yuglify (via npm)
RUN apt install -y npm && npm install -g yuglify

# Install libyaml (for watchdog)
RUN apt install -y libyaml-dev

# Copy across the requirements.txt file and install the requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all of the current code to the /app/ directory
COPY . /app/

# Make sure start.sh is executable
RUN chmod +x /app/start.sh

# Make sure that the celery scripts are executable
RUN chmod +x /app/.celery/*.sh

# Homebooru environment variables
# Scanner
ENV SCANNER_ENABLE_DIR_WATCHER=True
ENV SCANNER_ENABLE_AUTO_SCAN_ALL=True
ENV DIRECTORY_SCAN_ENABLED=True

# Homebooru
ENV ROLL_SECRET=False
ENV SECRET_KEY=changemenow!
ENV LOAD_FIXTURES=True
ENV STATIC_ROOT=/static/
ENV INSTALL_JQUERY=True
ENV DB_MIGRATE=True
ENV WORKERS=16
ENV BOORU_ANON_COMMENTS=True

# Debug
ENV UNIT_TEST_DISPLAY_COVERAGE=True
ENV BOORU_SHOW_FFMPEG_OUTPUT=False

# Celery
ENV CELERY_WORKERS=8

# Run the start.sh script with bash
CMD "/app/start.sh"