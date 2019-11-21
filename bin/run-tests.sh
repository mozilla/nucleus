#!/bin/bash -ex

flake8 nucleus
urlwait
python manage.py makemigrations | grep "No changes detected"
bin/post-deploy.sh
python manage.py test
