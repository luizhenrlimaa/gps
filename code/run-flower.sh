#!/bin/sh

cd /code

until python check_database.py; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

celery -A proj flower --basic_auth=admin:"admin"
