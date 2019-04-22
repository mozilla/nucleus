from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.http import HttpResponse

from rest_framework.authtoken.views import obtain_auth_token
from watchman import views as watchman_views


admin.site.site_header = 'Release Notes Administration'
admin.site.site_title = 'Release Notes Administration'

urlpatterns = [
    path('', include('nucleus.base.urls')),
    path('admin/', admin.site.urls),
    path('api-token-auth/', obtain_auth_token),
    path('rna/', include('nucleus.rna.urls')),

    path('robots.txt', lambda r: HttpResponse(
         "User-agent: *\n%s: /" % ('Allow' if settings.ENGAGE_ROBOTS else 'Disallow'),
         content_type="text/plain")),
    path('healthz/', watchman_views.ping, name="watchman.ping"),
    path('readiness/', watchman_views.status, name="watchman.status"),
]

if settings.OIDC_ENABLE:
    urlpatterns.append(path('oidc/', include('mozilla_django_oidc.urls')))
