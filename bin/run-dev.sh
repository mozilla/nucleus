#!/bin/sh

urlwait
bin/post-deploy.sh
python manage.py runserver 0.0.0.0:8000
