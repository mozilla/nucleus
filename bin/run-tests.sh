#!/bin/bash -ex
ruff check .
ruff format --check .
urlwait
python manage.py makemigrations | grep "No changes detected"
bin/post-deploy.sh
py.test
