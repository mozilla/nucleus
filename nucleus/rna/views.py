# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.http import parse_http_date_safe
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from django.views.decorators.http import last_modified, require_safe

from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet

from nucleus.rna.models import Note, Release
from nucleus.rna.serializers import NoteSerializer, ReleaseSerializer
from nucleus.rna.utils import HttpResponseJSON, get_last_modified_date

RNA_JSON_CACHE_TIME = getattr(settings, "RNA_JSON_CACHE_TIME", 600)


def auth_token(request):
    if request.user.is_active and request.user.is_staff:
        token, created = Token.objects.get_or_create(user=request.user)
        return HttpResponse(content=json.dumps({"token": token.key}), content_type="application/json")
    else:
        return HttpResponseForbidden()


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


class ReleaseViewSet(ModelViewSet):
    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer


class NestedNoteView(generics.ListAPIView):
    model = Note
    serializer_class = NoteSerializer

    def get_queryset(self):
        release = get_object_or_404(Release, pk=self.kwargs.get("pk"))
        return release.note_set.all()


@cache_page(RNA_JSON_CACHE_TIME)
@last_modified(get_last_modified_date)
@require_safe
def export_json(request):
    if request.GET.get("all") == "true":
        return HttpResponseJSON(Release.objects.all_as_list(), cors=True)

    mod_date = parse_http_date_safe(request.headers.get("If-Modified-Since"))
    if mod_date:
        mod_date = datetime.datetime.fromtimestamp(mod_date, datetime.UTC)
    else:
        mod_date = now() - datetime.timedelta(days=30)

    return HttpResponseJSON(Release.objects.recently_modified_list(mod_date=mod_date), cors=True)
