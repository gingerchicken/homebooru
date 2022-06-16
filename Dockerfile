FROM python:3

# Enviroment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Make the current working dir /code
WORKDIR /code

# Install ffmpeg
RUN apt update
RUN apt install -y ffmpeg

# Install magiclib
RUN apt install -y libmagic1

# Copy across the requirements.txt file and install the requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all of the current code to the /code directory
COPY . /code/

# Make sure start.sh is executable
RUN chmod +x /code/start.sh

# Run the start.sh script with bash
CMD "/code/start.sh"