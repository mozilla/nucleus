#!/bin/sh

./bin/post-deploy.sh
mkdir -p static
echo "$GIT_SHA" > static/revision.txt
uwsgi --ini /app/bin/uwsgi.ini