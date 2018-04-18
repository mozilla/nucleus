import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from .models import Note, Release


def get_last_modified_date(*args, **kwargs):
    """Returns the date of the last modified Note or Release.

    For use with Django's last_modified decorator.
    """
    try:
        latest_note = Note.objects.latest()
        latest_release = Release.objects.latest()
    except ObjectDoesNotExist:
        return None

    return max(latest_note.modified, latest_release.modified)


def migrate_versions():
    for r in Release.objects.filter(version__endswith='.0.0').only(
            'channel', 'version'):
        if r.channel == 'Release':
            Release.objects.filter(id=r.id).update(version=r.version[:-2])
        elif r.channel == 'Aurora':
            Release.objects.filter(id=r.id).update(version=r.version[:-2] + 'a2')
        elif r.channel == 'Beta':
            Release.objects.filter(id=r.id).update(version=r.version[:-2] + 'beta')


def get_duplicate_product_versions():
    version_ids = {}
    duplicates = {}
    for product in Release.PRODUCTS:
        version_ids[product] = {}
        for r in Release.objects.filter(product=product):
            version_ids[product].setdefault(r.version, [])
            version_ids[product][r.version].append(r.id)
            if len(version_ids[product][r.version]) > 1:
                duplicates[(product, r.version)] = version_ids[product][
                    r.version]
    return duplicates


class HttpResponseJSON(HttpResponse):
    def __init__(self, data, status=None, cors=False):
        super(HttpResponseJSON, self).__init__(content=json.dumps(data),
                                               content_type='application/json',
                                               status=status)

        if cors:
            self['Access-Control-Allow-Origin'] = '*'
