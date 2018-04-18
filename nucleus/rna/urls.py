# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.conf.urls import url, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('notes', views.NoteViewSet)
router.register('releases', views.ReleaseViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^releases/(?P<pk>\d+)/notes/$', views.NestedNoteView.as_view()),
    url(r'^auth_token/$', views.auth_token),
    url(r'^sync/?$', views.rnasync),
    url(r'^all-releases\.json$', views.export_json),
]
