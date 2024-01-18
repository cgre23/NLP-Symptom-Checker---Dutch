# Use an official Python runtime as the base image
FROM python:3.9-slim as build

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory (our Flask app) into the container at /app
COPY . /app

# Install Flask and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5050 available for the app
EXPOSE 5050

# Run the command to start the Flask app
CMD ["python", "app.py"]