import os
import site

try:
    import newrelic.agent
except ImportError:
    newrelic = None


os.environ.setdefault('CELERY_LOADER', 'django')
# NOTE: you can also set DJANGO_SETTINGS_MODULE in your environment to override
# the default value in manage.py

# Add the app dir to the python path so we can import manage.
wsgidir = os.path.dirname(__file__)
project_dir = os.path.abspath(os.path.join(wsgidir, '../'))
site.addsitedir(project_dir)

if newrelic and 'NEW_RELIC_LICENSE_KEY' in os.environ:
    newrelic.agent.initialize(os.path.join(project_dir, 'newrelic.ini'))

# manage adds /apps, /lib, and /vendor to the Python path.
import manage

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# vim: ft=python
