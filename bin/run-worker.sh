#!/bin/sh

urlwait
exec python manage.py spinach --threads 1
