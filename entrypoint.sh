#!/bin/sh

echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
# БУЛО: my_project.wsgi
# СТАЛО: config.wsgi (бо твоя папка з налаштуваннями називається config)
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000