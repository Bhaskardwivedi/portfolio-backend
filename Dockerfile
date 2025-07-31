# Use official Python image
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --break-system-packages -r requirements.txt

# Port setup
ENV PORT=8000
EXPOSE 8000

# Run using gunicorn
CMD ["sh", "-c", "gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT"]
