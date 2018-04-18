from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class HostnameMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super(HostnameMiddleware, self).__init__(get_response)
        values = [getattr(settings, x) for x in ['HOSTNAME', 'DEIS_APP',
                                                 'DEIS_RELEASE', 'DEIS_DOMAIN']]
        self.backend_server = '.'.join(x for x in values if x)

    def process_response(self, request, response):
        response['X-Backend-Server'] = self.backend_server
        return response
