# flake8: noqa
"""
WSGI config for nucleus project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""
# newrelic.agent must be imported and initialized first
# https://docs.newrelic.com/docs/agents/python-agent/installation/python-agent-advanced-integration#manual-integration
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleus.settings')  # NOQA

from django.core.handlers.wsgi import WSGIRequest
from django.core.wsgi import get_wsgi_application

from decouple import config


IS_HTTPS = config('HTTPS', default='off', cast=bool)


class WSGIHTTPSRequest(WSGIRequest):
    def _get_scheme(self):
        if IS_HTTPS:
            return 'https'

        return super(WSGIHTTPSRequest, self)._get_scheme()


application = get_wsgi_application()
application.request_class = WSGIHTTPSRequest

if config('SENTRY_DSN', None):
    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
    application = Sentry(application)

newrelic_license_key = config('NEW_RELIC_LICENSE_KEY', default=None)
if newrelic_license_key:
    application = newrelic.agent.WSGIApplicationWrapper(application)
