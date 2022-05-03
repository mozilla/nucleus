import json
from datetime import timedelta

from django.test import RequestFactory, TestCase
from django.utils.http import http_date
from django.utils.timezone import now

from nucleus.rna.models import Note, Release
from nucleus.rna.views import export_json


class TestExportJSON(TestCase):
    def setUp(self):
        over_20_days = now() - timedelta(days=22)
        over_30_days = now() - timedelta(days=32)
        over_40_days = now() - timedelta(days=42)
        self.r1 = Release.objects.create(
            product="Firefox",
            channel="Nightly",
            version="87.0a2",
            release_date=now(),
        )
        self.r2 = Release.objects.create(
            product="Firefox",
            channel="Nightly",
            version="88.0a2",
            release_date=now(),
        )
        # modified now
        self.r3 = Release.objects.create(
            product="Firefox",
            channel="Nightly",
            version="89.0a2",
            release_date=now(),
        )
        self.r1.modified = over_40_days
        self.r1.save(modified=False)
        self.r2.modified = over_30_days
        self.r2.save(modified=False)
        self.r3.modified = over_20_days
        self.r3.save(modified=False)
        self.rf = RequestFactory()

    def test_recently_modified_release(self):
        """Should only return releases modified more recently than 30 days ago"""
        resp = export_json(self.rf.get("/"))
        data = json.loads(resp.content)
        release_versions = [o["version"] for o in data]
        assert self.r1.version not in release_versions
        assert self.r2.version not in release_versions
        assert self.r3.version in release_versions

    def test_if_modified_since(self):
        """Should only return releases modified more recently than last-modified param"""
        over_30_days_ago = now() - timedelta(days=34)
        header_date = http_date(over_30_days_ago.timestamp())
        resp = export_json(self.rf.get("/", HTTP_IF_MODIFIED_SINCE=header_date))
        data = json.loads(resp.content)
        release_versions = [o["version"] for o in data]
        assert self.r1.version not in release_versions
        assert self.r2.version in release_versions
        assert self.r3.version in release_versions

    def test_if_modified_since_not_modified(self):
        """Should return an empty list if nothing has been modified since"""
        header_date = http_date(now().timestamp())
        resp = export_json(self.rf.get("/", HTTP_IF_MODIFIED_SINCE=header_date))
        data = json.loads(resp.content)
        assert data == []

    def test_invalid_if_modified_since_header(self):
        """Should go back to 14 day default if param is not ISO date"""
        header_date = "this is our concern Dude"
        resp = export_json(self.rf.get("/", HTTP_IF_MODIFIED_SINCE=header_date))
        data = json.loads(resp.content)
        release_versions = [o["version"] for o in data]
        assert self.r1.version not in release_versions
        assert self.r2.version not in release_versions
        assert self.r3.version in release_versions

    def test_recently_modified_note(self):
        """Should also return releases with notes modified more recently than 14 days ago"""
        self.r1.note_set.create(note="The Dude minds, man")
        resp = export_json(self.rf.get("/"))
        data = json.loads(resp.content)
        release_versions = [o["version"] for o in data]
        assert self.r1.version in release_versions
        assert self.r2.version not in release_versions
        assert self.r3.version in release_versions

    def test_recently_modified_note_distinct(self):
        """Should also return releases with notes modified more recently than 14 days ago"""
        note = Note.objects.create(note="The Dude minds, man")
        note2 = Note.objects.create(note="Careful, man, there’s a beverage here.")
        self.r1.note_set.add(note)
        self.r1.note_set.add(note2)
        resp = export_json(self.rf.get("/"))
        data = json.loads(resp.content)
        release_versions = [o["version"] for o in data]
        assert self.r1.version in release_versions
        assert self.r2.version not in release_versions
        assert self.r3.version in release_versions
        assert len(release_versions) == 2

    def test_recently_modified_fixed_in_note(self):
        """Should also return releases with notes modified more recently than 14 days ago"""
        self.r2.fixed_note_set.create(note="The Dude minds, man")
        resp = export_json(self.rf.get("/"))
        data = json.loads(resp.content)
        release_versions = [o["version"] for o in data]
        assert self.r1.version not in release_versions
        assert self.r2.version in release_versions
        assert self.r3.version in release_versions

    def test_all_as_list(self):
        """Should return all releases with no dupes"""
        note = Note.objects.create(note="The Dude minds, man")
        note2 = Note.objects.create(note="Careful, man, there’s a beverage here.")
        self.r1.note_set.add(note)
        self.r1.note_set.add(note2)
        resp = export_json(self.rf.get("/", {"all": "true"}))
        data = json.loads(resp.content)
        release_versions = [o["version"] for o in data]
        assert self.r1.version in release_versions
        assert self.r2.version in release_versions
        assert self.r3.version in release_versions
        assert len(release_versions) == 3
