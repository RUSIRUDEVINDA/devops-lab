# syntax=docker/dockerfile:1

# Build an image with the Python 3.12 image
FROM python:3.12-alpine

# Set the working directory to `/code`
WORKDIR /app

# Set environment variables used by the `flask` command
ENV FLASK_APP=demo.py
ENV FLASK_RUN_HOST=0.0.0.0

# Install `gcc` and other dependencies
RUN apk add --no-cache gcc musl-dev linux-headers

# Copy `requirements.txt`
COPY python/requirements.txt requirements.txt

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy python/demo.py to the workdir as app.py
COPY python/demo.py demo.py

EXPOSE 5000

# Set the default command for the container to `flask run --debug`
CMD ["flask", "run", "--debug"]