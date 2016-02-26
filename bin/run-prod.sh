#!/bin/sh

bin/run-common.sh

echo "$GIT_SHA" > static/revision.txt

exec gunicorn nucleus.wsgi:application -w ${WSGI_NUM_WORKERS:-2} -b 0.0.0.0:${PORT:-8000} \
    --log-file - --log-level ${GUNICORN_LOG_LEVEL:-info}
