FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install --break-system-packages -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT}"]
