#!/bin/bash -ex
ruff check .
black --check .
urlwait
python manage.py makemigrations | grep "No changes detected"
bin/post-deploy.sh
py.test
