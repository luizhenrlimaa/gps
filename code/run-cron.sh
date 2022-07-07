#!/bin/bash

#if [[ $(crontab -l | egrep -v "^(#|$)" | grep -q "/usr/local/bin/python /code/source/manage.py run_tasks"; echo $?) == 1 ]]
#then
#    echo "
#*/1 * * * * /usr/local/bin/python /code/source/manage.py run_tasks
#*/1 * * * * /usr/local/bin/python /code/source/manage.py finish_celery_groups
#" | crontab -
#
#fi
#
#cd /code/source
#
#until python test_database.py; do
#  echo "--- CRON --- Database is unavailable - sleeping"
#  sleep 1
#done
#
#sleep 5
#echo "--- CRON --- Schedule Tasks running on CRONTAB"
#
#service cron start
#
##/usr/local/bin/python /code/source/manage.py alarm_listeners &
#
#while true
#do
#	sleep 60
#    echo "--- CRON --- Running"
#done
#
#
