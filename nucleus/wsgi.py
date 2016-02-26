"""
WSGI config for nucleus project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleus.settings')  # NOQA

from django.conf import settings
from django.core.wsgi import get_wsgi_application

from decouple import config
from whitenoise.django import DjangoWhiteNoise

newrelic_ini = config('NEW_RELIC_CONFIG_FILE', default='newrelic.ini')
newrelic_license_key = config('NEW_RELIC_LICENSE_KEY', default=None)
if newrelic_ini and newrelic_license_key:
    import newrelic.agent
    newrelic.agent.initialize(newrelic_ini)


application = get_wsgi_application()
application = DjangoWhiteNoise(application)

# Add media files
if settings.MEDIA_ROOT and settings.MEDIA_URL:
    application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)

if newrelic_ini and newrelic_license_key:
    application = newrelic.agent.WSGIApplicationWrapper(application)
