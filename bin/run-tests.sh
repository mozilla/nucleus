#!/bin/bash

urlwait
bin/post-deploy.sh
python manage.py test
