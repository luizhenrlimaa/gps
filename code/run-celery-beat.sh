#!/bin/sh

cd /code

until python check_database.py; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

rm -f celerybeat.pid celerybeat-schedule
celery -A proj beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
