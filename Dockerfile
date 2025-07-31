# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy everything
COPY . /app

# Install requirements
RUN pip install --upgrade pip
RUN pip install --break-system-packages -r requirements.txt

# Expose default port
EXPOSE 8000

# Use Railway-injected PORT env
CMD ["sh", "-c", "gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT}"]
