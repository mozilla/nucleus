import json
from logging import getLogger

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils.timezone import now

from crum import get_current_user
from django_extensions.db.fields import CreationDateTimeField

from nucleus.base.tasks import tasks


log = getLogger(__name__)
M2M_ACTIONS = ['post_add', 'post_remove', 'post_clear']
DEFAULT_BRANCH = settings.GITHUB_OUTPUT_BRANCH


def send_instance_to_github(instance, branch=DEFAULT_BRANCH):
    log.debug(f'send_instance_to_github, {instance._meta.label_lower}, {instance.pk}')
    author = get_current_user()
    tasks.schedule('nucleus:save_to_github',
                   instance._meta.label_lower,  # app_name.model_name
                   instance.pk,
                   author.pk if author else None,
                   branch)


@receiver(post_save, weak=False, dispatch_uid='send_to_github_signal')
def send_to_github_signal(sender, instance, **kwargs):
    if issubclass(sender, SaveToGithubModel):
        log.debug(f'send_to_github_signal, {sender._meta}, {instance.pk}')
        instance.to_github()


@receiver(m2m_changed, weak=False, dispatch_uid='send_to_github_m2m')
def send_to_github_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    log.debug(f'send_to_github_m2m, {model._meta}, {action}, {pk_set}')
    if action in M2M_ACTIONS and issubclass(model, SaveToGithubModel):
        for obj in model.objects.filter(pk__in=pk_set):
            obj.to_github()


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
        super().save(*args, **kwargs)


class SaveToGithubModel(TimeStampedModel):
    """
    Abstract model class that adds support for outputting JSON files.

    Class must define:
    - a `to_dict()` method
    - a `slug` field for unique file naming
    - a `git_path` variable for the path within the git repo for the files of the model's type
        if not defined it will be the verbose plural name of the model
    """
    related_field_to_github = None

    class Meta:
        abstract = True

    @property
    def git_path(self):
        """Return a string path within the output git repo for files of this type"""
        return str(self._meta.verbose_name_plural)

    @property
    def json_file_path(self):
        return '/'.join((self.git_path, f'{self.slug}.json'))

    def to_json(self):
        """Return a JSON encoded string of the data from to_dict()"""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    def to_github(self):
        if self.related_field_to_github:
            field = getattr(self, self.related_field_to_github)
            for obj in field.all():
                obj.to_github()
        else:
            send_instance_to_github(self)
