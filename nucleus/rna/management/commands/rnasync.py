from django.conf import settings
from django.core.management import BaseCommand

from synctool.functions import sync_data

from nucleus.rna.utils import get_last_modified_date


DEFAULT_RNA_SYNC_URL = 'https://nucleus.mozilla.org/rna/sync/'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-u', '--url',
                            default=getattr(settings, 'RNA_SYNC_URL', DEFAULT_RNA_SYNC_URL),
                            help='Full URL to RNA Sync endpoint')
        parser.add_argument('-c', '--clean', action='store_true',
                            help='Delete all RNA data before sync.')
        parser.add_argument('--database', default='default',
                            help=('Specifies the database to use, if using a db. '
                                  'Defaults to "default".')),

    def handle(self, *args, **options):
        clean = options['clean']
        sync_data(url=options['url'],
                  clean=clean,
                  last_modified=None if clean else get_last_modified_date(),
                  api_token=None)
