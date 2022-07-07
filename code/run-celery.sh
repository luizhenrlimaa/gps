#!/bin/sh

cd /code

# Wait for database ready

until python check_database.py; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

full_ip_addr=$(hostname -i)
ip_addr=${full_ip_addr%% *}
worker_group=${WORKER_GROUP_NAME}
min_concurrency=${MIN_CONCURRENCY}
max_concurrency=${MAX_CONCURRENCY}
memory=${MEMORY_LIMIT}
queues=${QUEUES}

echo "celery -A proj worker -Ofair --loglevel=INFO -n ${worker_group}@${ip_addr} -Q ${queues} --autoscale=${max_concurrency},${min_concurrency} --max-memory-per-child=${memory}"

celery -A proj worker -Ofair --loglevel=INFO -n ${worker_group}@${ip_addr} -Q ${queues} --autoscale=${max_concurrency},${min_concurrency} --max-memory-per-child=${memory}
