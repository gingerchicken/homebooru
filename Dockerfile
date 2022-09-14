FROM python:3

# Enviroment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Celery
ENV CELERY=True
ENV CELERY_WORKERS=5

# Make the current working dir /app
WORKDIR /app

# Install ffmpeg
RUN apt update
RUN apt install -y ffmpeg

# Install magiclib
RUN apt install -y libmagic1

# Install yuglify (via npm)
RUN apt install -y npm && npm install -g yuglify

# Copy across the requirements.txt file and install the requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all of the current code to the /app/ directory
COPY . /app/

# Make sure start.sh is executable
RUN chmod +x /app/start.sh

# Run the start.sh script with bash
CMD "/app/start.sh"