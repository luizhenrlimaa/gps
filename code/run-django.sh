#!/bin/sh

cd /code

until python check_database.py; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

python manage.py migrate
if [ -f IGNORE_COLLECTSTATIC.txt ]; then echo 'Ignoring collectstatic...' ; else python manage.py collectstatic --noinput; fi;

gunicorn proj.wsgi:application --limit-request-line 0 --worker-tmp-dir /dev/shm --preload --config gunicorn_hooks.py --timeout 900 -w 17 -b :8000
