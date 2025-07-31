FROM python:3.10-slim

WORKDIR /app

COPY . /app

# Upgrade pip and install packages
RUN pip install --upgrade pip
RUN pip install --break-system-packages -r requirements.txt

# Define PORT explicitly (Railway sets it automatically too, but for safety we default it)
ENV PORT=8000
EXPOSE 8000

# Run Django using gunicorn on the specified port
CMD exec gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 3
