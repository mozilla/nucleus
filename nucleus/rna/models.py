# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from itertools import chain

from django.conf import settings
from django.db import models
from django.forms.models import model_to_dict
from django.utils.text import slugify
from django.utils.timezone import now
from django_extensions.db.fields import CreationDateTimeField


class TimeStampedModel(models.Model):
    """
    Replacement for django_extensions.db.models.TimeStampedModel
    that updates the modified timestamp by default, but allows
    that behavior to be overridden by passing a modified=False
    parameter to the save method
    """
    created = CreationDateTimeField()
    modified = models.DateTimeField(editable=False, blank=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if kwargs.pop('modified', True):
            self.modified = now()
        super(TimeStampedModel, self).save(*args, **kwargs)


class ReleaseManager(models.Manager):
    def all_as_list(self):
        """Return all releases as a list of dicts"""
        return [r.to_dict() for r in self.prefetch_related('note_set').all()]


class Release(TimeStampedModel):
    CHANNELS = ('Nightly', 'Aurora', 'Beta', 'Release', 'ESR')
    PRODUCTS = ('Firefox', 'Firefox for Android',
                'Firefox Extended Support Release', 'Firefox OS',
                'Thunderbird', 'Firefox for iOS')

    product = models.CharField(max_length=255,
                               choices=[(p, p) for p in PRODUCTS])
    channel = models.CharField(max_length=255,
                               choices=[(c, c) for c in CHANNELS])
    version = models.CharField(max_length=255)
    release_date = models.DateTimeField()
    text = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    bug_list = models.TextField(blank=True)
    bug_search_url = models.CharField(max_length=2000, blank=True)
    system_requirements = models.TextField(blank=True)

    objects = ReleaseManager()

    @property
    def slug(self):
        product = slugify(self.product)
        channel = self.channel.lower()
        if product.lower() == 'firefox-extended-support-release':
            product = 'firefox'
            channel = 'esr'
        return '-'.join([product, self.version, channel])

    def major_version(self):
        return self.version.split('.', 1)[0]

    def get_bug_search_url(self):
        if self.bug_search_url:
            return self.bug_search_url

        if self.product == 'Thunderbird':
            return (
                'https://bugzilla.mozilla.org/buglist.cgi?'
                'classification=Client%20Software&query_format=advanced&'
                'bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&'
                'target_milestone=Thunderbird%20{version}.0&product=Thunderbird'
                '&resolution=FIXED'
            ).format(version=self.major_version())

        return (
            'https://bugzilla.mozilla.org/buglist.cgi?'
            'j_top=OR&f1=target_milestone&o3=equals&v3=Firefox%20{version}&'
            'o1=equals&resolution=FIXED&o2=anyexact&query_format=advanced&'
            'f3=target_milestone&f2=cf_status_firefox{version}&'
            'bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&'
            'v1=mozilla{version}&v2=fixed%2Cverified&limit=0'
        ).format(version=self.major_version())

    def equivalent_release_for_product(self, product):
        """
        Returns the release for a specified product with the same
        channel and major version with the highest minor version,
        or None if no such releases exist
        """
        releases = self._default_manager.filter(
            version__startswith=self.major_version() + '.',
            channel=self.channel, product=product).order_by('-version')
        if not getattr(settings, 'DEV', False):
            releases = releases.filter(is_public=True)
        if releases:
            return sorted(
                sorted(releases, reverse=True,
                       key=lambda r: len(r.version.split('.'))),
                reverse=True, key=lambda r: r.version.split('.')[1])[0]

    def equivalent_android_release(self):
        if self.product == 'Firefox':
            return self.equivalent_release_for_product('Firefox for Android')

    def equivalent_desktop_release(self):
        if self.product == 'Firefox for Android':
            return self.equivalent_release_for_product('Firefox')

    def notes(self, public_only=False):
        """
        Retrieve a list of Note instances that should be shown for this
        release, grouped as either new features or known issues, and sorted
        first by sort_num highest to lowest and then by created date,
        which is applied to both groups,
        and then for new features we also sort by tag in the order specified
        by Note.TAGS, with untagged notes coming first, then finally moving
        any note with the fixed tag that starts with the release version to
        the top, for what we call "dot fixes".
        """
        tag_index = dict((tag, i) for i, tag in enumerate(Note.TAGS))
        notes = self.note_set.order_by('-sort_num', 'created')
        if public_only:
            notes = notes.filter(is_public=True)
        known_issues = [n for n in notes if n.is_known_issue_for(self)]
        new_features = sorted(
            sorted(
                (n for n in notes if not n.is_known_issue_for(self)),
                key=lambda note: tag_index.get(note.tag, 0)),
            key=lambda n: n.tag == 'Fixed' and n.note.startswith(self.version),
            reverse=True)

        return new_features, known_issues

    def to_dict(self):
        """Return a dict all all data about the release"""
        data = model_to_dict(self, exclude=['id'])
        data['title'] = unicode(self)
        data['slug'] = self.slug
        data['release_date'] = self.release_date.date().isoformat()
        data['created'] = self.created.isoformat()
        data['modified'] = self.modified.isoformat()
        new_features, known_issues = self.notes(public_only=False)
        for note in known_issues:
            note.tag = 'Known'
        data['notes'] = [n.to_dict(self) for n in chain(new_features, known_issues)]
        return data

    def to_simple_dict(self):
        """Return a dict of only the basic data about the release"""
        return {
            'version': self.version,
            'product': self.product,
            'channel': self.channel,
            'is_public': self.is_public,
            'slug': self.slug,
            'title': unicode(self),
        }

    def __unicode__(self):
        return '{product} {version} {channel}'.format(
            product=self.product, version=self.version, channel=self.channel)

    class Meta:
        # TODO: see if this has a significant performance impact
        ordering = ('product', '-version', 'channel')
        unique_together = (('product', 'version'),)
        get_latest_by = 'modified'


class Note(TimeStampedModel):
    TAGS = ('New', 'Changed', 'HTML5', 'Feature', 'Language', 'Developer',
            'Fixed')

    bug = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    releases = models.ManyToManyField(Release, blank=True)
    is_known_issue = models.BooleanField(default=False)
    fixed_in_release = models.ForeignKey(Release, null=True, blank=True,
                                         related_name='fixed_note_set')
    tag = models.CharField(max_length=255, blank=True,
                           choices=[(t, t) for t in TAGS])
    sort_num = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)

    def is_known_issue_for(self, release):
        return self.is_known_issue and self.fixed_in_release != release

    def to_dict(self, release=None):
        data = model_to_dict(self, exclude=[
            'releases',
            'is_known_issue',
        ])
        data['created'] = self.created.isoformat()
        data['modified'] = self.modified.isoformat()
        if self.fixed_in_release:
            data['fixed_in_release'] = self.fixed_in_release.to_simple_dict()
        else:
            del data['fixed_in_release']

        if release and self.is_known_issue_for(release):
            data['tag'] = 'Known'

        return data

    def __unicode__(self):
        return self.note

    class Meta:
        get_latest_by = 'modified'
