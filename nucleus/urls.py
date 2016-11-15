from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse


admin.autodiscover()  # Discover admin.py files for the admin interface.

urlpatterns = [
    url(r'', include('nucleus.base.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-token-auth/',
        'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^rna/', include('rna.urls')),

    url(r'^robots\.txt$', lambda r: HttpResponse(
        "User-agent: *\n%s: /" % ('Allow' if settings.ENGAGE_ROBOTS else 'Disallow'),
        content_type="text/plain")),
]

if settings.SAML_ENABLE:
    urlpatterns.append(url(r'^saml2/', include('nucleus.saml.urls')))
