from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now

from nucleus.rna.models import Country, Note, Release


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

    def test_distinct_recently_modified(self):
        note = Note.objects.create(note="The Dude minds, man")
        note2 = Note.objects.create(note="Careful, man, there’s a beverage here.")
        self.r3.note_set.add(note)
        self.r2.note_set.add(note)
        self.r3.note_set.add(note2)
        data = Release.objects.recently_modified_list(days_ago=5)
        versions = [o["version"] for o in data]
        assert self.r1.version not in versions
        assert self.r2.version in versions
        assert self.r3.version in versions
        assert len(versions) == 2


class TestNote(TestCase):
    def test_to_dict__simple__no_relations(self):
        # Very simple test of the to_dict() method, mainly
        # to prove that progressive_rollout is included
        data = dict(
            bug=1234,
            note="Test note",
            tag="this is a tag",
            sort_num=1,
            is_public=True,
            progressive_rollout=True,
        )

        note = Note(**data)
        note.save()

        dumped_dict = note.to_dict()
        for key in [
            "bug",
            "note",
            "tag",
            "sort_num",
            "is_public",
            "progressive_rollout",
        ]:
            assert dumped_dict[key] == data[key]

        assert "created" in dumped_dict
        assert "modified" in dumped_dict

    def test_to_dict__relevant_country_field(self):
        # Country data is bootstrapped by a data migration

        iceland = Country.objects.get(code="IS")
        india = Country.objects.get(code="IN")

        data = dict(
            bug=1234,
            note="Test note",
            tag="this is a tag",
            sort_num=1,
            is_public=True,
            progressive_rollout=True,
        )

        note = Note(**data)
        note.save()

        assert note.relevant_countries.count() == 0
        dumped_dict = note.to_dict()
        assert dumped_dict["relevant_countries"] == []

        note.relevant_countries.add(india)
        note.relevant_countries.add(iceland)
        assert note.relevant_countries.count() == 2

        dumped_dict = note.to_dict()
        assert dumped_dict["relevant_countries"] == [
            {"name": "Iceland", "code": "IS"},
            {"name": "India", "code": "IN"},
        ]
