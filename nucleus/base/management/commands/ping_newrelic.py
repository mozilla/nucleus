import os
import os.path

from django.conf import settings
from django.core.management.base import CommandError, NoArgsCommand

import urllib
import urllib2


GITHUB_URL = 'https://github.com/mozilla/nucleus/'
NEW_RELIC_URL = 'https://rpm.newrelic.com/deployments.xml'
NEW_RELIC_API_KEY = os.getenv('NEW_RELIC_API_KEY', None)
NEW_RELIC_APP_NAME = os.getenv('NEW_RELIC_APP_NAME', None)
REV_FILE = settings.path('static', 'revision.txt')
PREV_REV_FILE = settings.path('static', 'prev-revision.txt')


class Command(NoArgsCommand):
    help = 'Inform New Relic of a deployment.'
    revision = None
    prev_revision = None

    def handle_noargs(self, **options):
        print 'Pinging New Relic.'
        if not (NEW_RELIC_API_KEY or NEW_RELIC_APP_NAME):
            raise CommandError('Please set NEW_RELIC_API_KEY and NEW_RELIC_APP_NAME '
                               'environment variables.')
        github_url = self.get_github_url()
        # TODO: Make description useful and get git hashes and change log.
        data = urllib.urlencode({
            'deployment[description]': 'Deployed to PaaS.',
            'deployment[revision]': self.revision,
            'deployment[app_name]': NEW_RELIC_APP_NAME,
            'deployment[changelog]': github_url,
        })
        headers = {'x-api-key': NEW_RELIC_API_KEY}
        try:
            request = urllib2.Request(NEW_RELIC_URL, data, headers)
            urllib2.urlopen(request)
        except urllib2.HTTPError as exp:
            raise CommandError('Error notifying New Relic: {0}'.format(exp))

    def get_github_url(self):
        compare_tmpl = 'compare/{0}...{1]'
        commit_tmpl = 'commit/{0}'
        fargs = []

        if os.path.exists(PREV_REV_FILE):
            url = GITHUB_URL + compare_tmpl
            with open(PREV_REV_FILE) as prf:
                self.prev_revision = prf.read()
                fargs.append(self.prev_revision)
        else:
            url = GITHUB_URL + commit_tmpl

        with open(REV_FILE) as rf:
            self.revision = rf.read()
            fargs.append(self.revision)

        return url.format(*fargs)
