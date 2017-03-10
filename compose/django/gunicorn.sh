#!/bin/sh
NEW_RELIC_CONFIG_FILE=/newrelic.ini
export NEW_RELIC_CONFIG_FILE

python /app/manage.py collectstatic --noinput
newrelic-admin run-program /usr/local/bin/gunicorn config.wsgi -w 4 -b 0.0.0.0:5000 --chdir=/app
