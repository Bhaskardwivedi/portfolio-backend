# Use a stable Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --break-system-packages -r requirements.txt

# Run Django using Gunicorn
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT}
