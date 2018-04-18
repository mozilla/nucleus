from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse

from rest_framework.authtoken.views import obtain_auth_token
from watchman import views as watchman_views


admin.autodiscover()  # Discover admin.py files for the admin interface.
admin.site.site_header = 'Release Notes Administration'
admin.site.site_title = 'Release Notes Administration'

urlpatterns = [
    url(r'', include('nucleus.base.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-token-auth/', obtain_auth_token),
    url(r'^rna/', include('nucleus.rna.urls')),

    url(r'^robots\.txt$', lambda r: HttpResponse(
        "User-agent: *\n%s: /" % ('Allow' if settings.ENGAGE_ROBOTS else 'Disallow'),
        content_type="text/plain")),
    url(r'^healthz/$', watchman_views.ping, name="watchman.ping"),
    url(r'^readiness/$', watchman_views.status, name="watchman.status"),
]

if settings.OIDC_ENABLE:
    urlpatterns.append(url(r'^oidc/', include('mozilla_django_oidc.urls')))
