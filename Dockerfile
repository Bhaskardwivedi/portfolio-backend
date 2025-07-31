FROM python:3.10-slim

WORKDIR /app

COPY . /app

# Install pip packages
RUN pip install --upgrade pip
RUN pip install --break-system-packages -r requirements.txt

# Railway will inject the PORT env variable
ENV PORT 8000
EXPOSE ${PORT}

# Run gunicorn with the correct port
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT}
