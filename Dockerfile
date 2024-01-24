# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install ffmpeg, libsm6, libxext6
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Run gunicorn as a non-root user using the WSGI app in app.py
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
