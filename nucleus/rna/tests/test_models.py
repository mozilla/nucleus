from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now

from nucleus.rna.models import Release


class TestReleaseQueries(TestCase):
    def setUp(self):
        one_week_ago = now() - timedelta(days=7)
        two_weeks_ago = now() - timedelta(days=14)
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
        self.r1.modified = two_weeks_ago
        self.r1.save(modified=False)
        self.r2.modified = one_week_ago
        self.r2.save(modified=False)

    def test_recently_modified_release(self):
        """Should only return releases modified more recently than `days_ago`"""
        data = Release.objects.recently_modified_list(days_ago=5)
        versions = [o["version"] for o in data]
        assert self.r1.version not in versions
        assert self.r2.version not in versions
        assert self.r3.version in versions

    def test_recently_modified_note(self):
        """Should also return releases with notes modified more recently than `days_ago`"""
        self.r1.note_set.create(note="The Dude minds, man")
        data = Release.objects.recently_modified_list(days_ago=5)
        versions = [o["version"] for o in data]
        assert self.r1.version in versions
        assert self.r2.version not in versions
        assert self.r3.version in versions

    def test_recently_modified_fixed_in_note(self):
        """Should also return releases with notes modified more recently than `days_ago`"""
        self.r2.fixed_note_set.create(note="The Dude minds, man")
        data = Release.objects.recently_modified_list(days_ago=5)
        versions = [o["version"] for o in data]
        assert self.r1.version not in versions
        assert self.r2.version in versions
        assert self.r3.version in versions
