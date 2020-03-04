#!/bin/sh

urlwait
exec newrelic-admin run-program python manage.py spinach --threads 1
