# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging

try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url
from django.core.exceptions import ImproperlyConfigured

from django_browserid import views
from django_browserid.util import import_from_setting


logger = logging.getLogger(__name__)


try:
    Verify = import_from_setting('BROWSERID_VERIFY_CLASS')
except ImproperlyConfigured as e:
    logger.info('Loading BROWSERID_VERIFY_CLASS failed: {0}.\nFalling back to default.'.format(e))
    Verify = views.Verify


urlpatterns = patterns('',
    url(r'^browserid/login/$', Verify.as_view(), name='browserid.login'),
    url(r'^browserid/logout/$', views.Logout.as_view(), name='browserid.logout'),
    url(r'^browserid/info/$', views.Info.as_view(), name='browserid.info'),
)
