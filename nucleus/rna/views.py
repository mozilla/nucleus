# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import last_modified, require_safe
from django.views.decorators.cache import cache_page

from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet
from synctool.routing import Route

from . import models, serializers
from .utils import get_last_modified_date, HttpResponseJSON


rnasync = Route(api_token=None).app('rna', 'rna')
rnasync = last_modified(get_last_modified_date)(rnasync)
RNA_JSON_CACHE_TIME = getattr(settings, 'RNA_JSON_CACHE_TIME', 600)


def auth_token(request):
    if request.user.is_active and request.user.is_staff:
        token, created = Token.objects.get_or_create(user=request.user)
        return HttpResponse(
            content=json.dumps({'token': token.key}),
            content_type='application/json')
    else:
        return HttpResponseForbidden()


class NoteViewSet(ModelViewSet):
    queryset = models.Note.objects.all()
    serializer_class = serializers.NoteSerializer


class ReleaseViewSet(ModelViewSet):
    queryset = models.Release.objects.all()
    serializer_class = serializers.ReleaseSerializer


class NestedNoteView(generics.ListAPIView):
    model = models.Note
    serializer_class = serializers.NoteSerializer

    def get_queryset(self):
        release = get_object_or_404(models.Release, pk=self.kwargs.get('pk'))
        return release.note_set.all()


@cache_page(RNA_JSON_CACHE_TIME)
@require_safe
def export_json(request):
    mod_date = request.GET.get('last-modified')
    if mod_date == 'all':
        return HttpResponseJSON(models.Release.objects.all_as_list())

    if mod_date:
        try:
            # parse_datetime can return None or raise ValueError if value is not parsable
            mod_date = parse_datetime(mod_date)
        except ValueError:
            mod_date = None

    if mod_date:
        query = models.Release.objects.recently_modified(mod_date=mod_date)
    else:
        query = models.Release.objects.recently_modified(days_ago=14)

    return HttpResponseJSON([o.to_dict() for o in query])
