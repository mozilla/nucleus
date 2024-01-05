#!/bin/bash -ex
black --check .
ruff check .
urlwait
python manage.py makemigrations | grep "No changes detected"
bin/post-deploy.sh
py.test
