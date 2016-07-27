from django.conf import settings


class HostnameMiddleware(object):
    def __init__(self):
        values = [getattr(settings, x) for x in ['HOSTNAME', 'DEIS_APP',
                                                 'DEIS_RELEASE', 'DEIS_DOMAIN']]
        self.backend_server = '.'.join(x for x in values if x)

    def process_response(self, request, response):
        response['X-Backend-Server'] = self.backend_server
        return response
