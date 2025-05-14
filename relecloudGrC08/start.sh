#!/bin/bash
echo "Starting server on port $PORT..."
python manage.py migrate --noinput
exec daphne -b 0.0.0.0 -p "$PORT" project.asgi:application
