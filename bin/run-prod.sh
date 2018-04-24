#!/bin/sh

echo "$GIT_SHA" > static/revision.txt
exec gunicorn nucleus.wsgi:application --bind "0.0.0.0:${PORT:-8000}" \
                          --workers "${WSGI_NUM_WORKERS:-4}" \
                          --worker-class "${WSGI_WORKER_CLASS:-meinheld.gmeinheld.MeinheldWorker}" \
                          --log-level "${WSGI_LOG_LEVEL:-info}" \
                          --error-logfile - \
                          --access-logfile -
