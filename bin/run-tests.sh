#!/bin/bash -ex

flake8 nucleus
urlwait
bin/post-deploy.sh
python manage.py test
