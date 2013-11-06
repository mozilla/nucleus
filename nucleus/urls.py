from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse

from funfactory.monkeypatches import patch


patch()  # Apply funfactory monkeypatches.
admin.autodiscover()  # Discover admin.py files for the admin interface.


urlpatterns = patterns('',
    # Example:
    (r'', include('nucleus.base.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^rna/', include('rna.urls')),

    (r'^robots\.txt$',
        lambda r: HttpResponse(
            "User-agent: *\n%s: /" % 'Allow' if settings.ENGAGE_ROBOTS else 'Disallow' ,
            mimetype="text/plain"
        )
    ),

)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
