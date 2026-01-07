FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Встановлюємо dos2unix
RUN apt-get update && apt-get install -y \
    gcc \
    dos2unix \
    && apt-get clean

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/
COPY entrypoint.sh /app/entrypoint.sh

# Цей рядок корисний, але docker-compose command його все одно перезапише (і це ок)
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]