import json
from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now

from nucleus.rna.models import Release


class TestExportJSON(TestCase):
    def setUp(self):
        four_weeks_ago = now() - timedelta(days=28)
        three_weeks_ago = now() - timedelta(days=21)
        self.r1 = Release.objects.create(
            product='Firefox',
            channel='Nightly',
            version='87.0a2',
            release_date=now(),
        )
        self.r2 = Release.objects.create(
            product='Firefox',
            channel='Nightly',
            version='88.0a2',
            release_date=now(),
        )
        # modified now
        self.r3 = Release.objects.create(
            product='Firefox',
            channel='Nightly',
            version='89.0a2',
            release_date=now(),
        )
        self.r1.modified = four_weeks_ago
        self.r1.save(modified=False)
        self.r2.modified = three_weeks_ago
        self.r2.save(modified=False)

    def test_recently_modified_release(self):
        """Should only return releases modified more recently than 14 days ago"""
        resp = self.client.get('/rna/all-releases.json')
        data = json.loads(resp.content)
        release_versions = [o['version'] for o in data]
        assert self.r1.version not in release_versions
        assert self.r2.version not in release_versions
        assert self.r3.version in release_versions

    def test_last_modified_param(self):
        """Should only return releases modified more recently than last-modified param"""
        over_three_weeks_ago = now() - timedelta(days=22)
        resp = self.client.get('/rna/all-releases.json',
                               {'last-modified': over_three_weeks_ago.isoformat()})
        data = json.loads(resp.content)
        release_versions = [o['version'] for o in data]
        assert self.r1.version not in release_versions
        assert self.r2.version in release_versions
        assert self.r3.version in release_versions

    def test_invalid_last_modified_param(self):
        """Should go back to 14 day default if param is not ISO date"""
        resp = self.client.get('/rna/all-releases.json',
                               {'last-modified': 'this is our concern Dude'})
        data = json.loads(resp.content)
        release_versions = [o['version'] for o in data]
        assert self.r1.version not in release_versions
        assert self.r2.version not in release_versions
        assert self.r3.version in release_versions

    def test_recently_modified_note(self):
        """Should also return releases with notes modified more recently than 14 days ago"""
        self.r1.note_set.create(note='The Dude minds, man')
        resp = self.client.get('/rna/all-releases.json')
        data = json.loads(resp.content)
        release_versions = [o['version'] for o in data]
        assert self.r1.version in release_versions
        assert self.r2.version not in release_versions
        assert self.r3.version in release_versions

    def test_recently_modified_fixed_in_note(self):
        """Should also return releases with notes modified more recently than 14 days ago"""
        self.r2.fixed_note_set.create(note='The Dude minds, man')
        resp = self.client.get('/rna/all-releases.json')
        data = json.loads(resp.content)
        release_versions = [o['version'] for o in data]
        assert self.r1.version not in release_versions
        assert self.r2.version in release_versions
        assert self.r3.version in release_versions
