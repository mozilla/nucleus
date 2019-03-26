import json
import os
from codecs import open
from shutil import rmtree

from django.conf import settings
from django.core.management import BaseCommand

from nucleus.rna.models import Release


if hasattr(settings, 'RNA_JSON_EXPORT_DIR'):
    OUTPUT_DIR = settings.RNA_JSON_EXPORT_DIR
else:
    OUTPUT_DIR = os.path.join(settings.ROOT, 'json_export')


def setup():
    rmtree(OUTPUT_DIR, ignore_errors=True)
    os.mkdir(OUTPUT_DIR)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # start fresh
        setup()
        releases = Release.objects.all_as_list()
        for rel in releases:
            with open(os.path.join(OUTPUT_DIR, '{}.json'.format(rel['slug'])),
                      'w', encoding='utf-8') as fp:
                json.dump(rel, fp, indent=2, sort_keys=True)

        print('Exported {} releases'.format(len(releases)))
