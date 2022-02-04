#!/bin/bash -ex

flake8 nucleus
black --check .
isort --check .
urlwait
python manage.py makemigrations | grep "No changes detected"
bin/post-deploy.sh
py.test
