#!/bin/bash -ex

flake8 nucleus
bin/post-deploy.sh
python manage.py test
