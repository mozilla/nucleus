#!/bin/bash -ex

urlwait
bin/post-deploy.sh
python manage.py test
