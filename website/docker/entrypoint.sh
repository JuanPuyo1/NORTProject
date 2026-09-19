#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py seed_blog_posts

exec gunicorn nort_site.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-60}"
