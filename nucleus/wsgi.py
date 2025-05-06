# flake8: noqa
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nucleus.settings")  # NOQA

from django.core.handlers.wsgi import WSGIRequest
from django.core.wsgi import get_wsgi_application

from decouple import config

IS_HTTPS = config("HTTPS", default="off", cast=bool)


class WSGIHTTPSRequest(WSGIRequest):
    def _get_scheme(self):
        if IS_HTTPS:
            return "https"

        return super()._get_scheme()


application = get_wsgi_application()
application.request_class = WSGIHTTPSRequest
