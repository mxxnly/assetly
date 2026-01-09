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
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# ЗМІНА 2: Виправляємо права саме для цієї копії
RUN dos2unix /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
