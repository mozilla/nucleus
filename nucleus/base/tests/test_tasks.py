from datetime import timedelta
from unittest.mock import patch

from django.apps import apps
from django.test import override_settings
from django.utils.timezone import now

import pytest
from crum import set_current_user
from github import UnknownObjectException

from nucleus.base import tasks
from nucleus.base.models import GithubLog


def get_modified_data():
    data = {
        'modified': 'yesterday',
        'name': 'Jeffry',
        'sister': 'Maud',
        'others': [
            {
                'name': 'Dude',
                'modified': 'yesterday',
            },
            {
                'name': 'Donnie',
                'modified': 'yesterday',
            },
        ],
        'bowling': {
            'when': 'Every day',
            'modified': 'yesterday',
        },
    }
    data_today = {
        'modified': 'today',
        'name': 'Jeffry',
        'sister': 'Maud',
        'others': [
            {
                'name': 'Dude',
                'modified': 'today',
            },
            {
                'name': 'Donnie',
                'modified': 'today',
            },
        ],
        'bowling': {
            'when': 'Every day',
            'modified': 'today',
        },
    }
    return data, data_today


def test_remove_modified():
    data, data_today = get_modified_data()
    assert data != data_today
    assert tasks.remove_modified(data) == tasks.remove_modified(data_today)

    # start with root level the same
    # ensure deeper objects tested
    del data['modified']
    del data_today['modified']
    assert data != data_today
    assert tasks.remove_modified(data) == tasks.remove_modified(data_today)


def test_data_matches():
    data, data_today = get_modified_data()
    assert tasks.data_matches(data, data_today)

    # start with root level the same
    # ensure deeper objects tested
    del data['modified']
    del data_today['modified']
    assert tasks.data_matches(data, data_today)


# increments for each time called for unique data
VERSION = 70


def get_version_str():
    global VERSION
    VERSION += 1
    return f'{VERSION}.0a1'


@override_settings(GITHUB_PUSH_ENABLE=True)
def setup_data():
    user_model = apps.get_model('auth.user')
    user = user_model.objects.create(
        username=get_version_str(),
        email='dude@example.com',
        first_name='The',
        last_name='Dude',
    )
    set_current_user(user)
    model = apps.get_model('rna.release')
    model.objects.create(
        product='Firefox',
        channel='Nightly',
        version=get_version_str(),
        release_date=now(),
    )
    return GithubLog.objects.latest()


@patch.object(tasks, 'github')
@pytest.mark.django_db
def test_save_to_github_update(gh_mock):
    ghl = setup_data()
    repo = gh_mock.get_repo()
    obj = ghl.content_object

    # with file already in github
    ghf = repo.get_contents()
    ghf.decoded_content = '{}'
    tasks.save_to_github(ghl.pk)
    repo.get_contents.assert_called_with(obj.json_file_path, ref=ghl.branch)
    gh_mock.get_author.assert_called_with(ghl.author)
    repo.update_file.assert_called_with(obj.json_file_path,
                                        f'Update {obj.json_file_path}',
                                        obj.to_json(),
                                        ghf.sha,
                                        branch=ghl.branch,
                                        author=gh_mock.get_author())


@patch.object(tasks, 'github')
@pytest.mark.django_db
def test_save_to_github_skip_update(gh_mock):
    """Should skip updating or creating if the data is the same"""
    ghl = setup_data()
    repo = gh_mock.get_repo()
    obj = ghl.content_object

    # with file already in github
    orig_json = obj.to_json()
    ghf = repo.get_contents()
    ghf.decoded_content = orig_json
    obj.save()  # update modified so that they're different
    new_json = obj.to_json()
    # should have different modified times
    assert new_json != orig_json
    tasks.save_to_github(ghl.pk)
    repo.get_contents.assert_called_with(obj.json_file_path, ref=ghl.branch)
    gh_mock.get_author.assert_called_with(ghl.author)
    repo.update_file.assert_not_called()
    repo.create_file.assert_not_called()


@patch.object(tasks, 'github')
@pytest.mark.django_db
def test_save_to_github_create(gh_mock):
    ghl = setup_data()
    repo = gh_mock.get_repo()
    obj = ghl.content_object

    # with no file already in github
    repo.get_contents.side_effect = UnknownObjectException('failed', 'missing', None)
    tasks.save_to_github(ghl.pk)
    repo.get_contents.assert_called_with(obj.json_file_path, ref=ghl.branch)
    gh_mock.get_author.assert_called_with(ghl.author)
    repo.create_file.assert_called_with(obj.json_file_path,
                                        f'Create {obj.json_file_path}',
                                        obj.to_json(),
                                        branch=ghl.branch,
                                        author=gh_mock.get_author())


@patch.object(tasks, 'tasks')
@pytest.mark.django_db
def test_cleanup_failures(tasks_mock):
    # setup two objects. only one should requeue.
    ghl = setup_data()
    setup_data()
    ghl.created = now() - timedelta(hours=2)
    ghl.save()
    tasks.cleanup()
    tasks_mock.schedule.assert_called_once_with(tasks.save_to_github, ghl.pk)


@patch.object(tasks, 'tasks')
@pytest.mark.django_db
def test_cleanup_max_failures(tasks_mock):
    ghl = setup_data()
    ghl.created = now() - timedelta(hours=2)
    ghl.save()
    # call 8 times
    for i in range(8):
        tasks.cleanup()

    # should only have re run it MAX_FAILS times
    ghl.refresh_from_db()
    assert ghl.fail_count == tasks.MAX_FAILS
    assert tasks_mock.schedule.call_count == tasks.MAX_FAILS


@patch.object(tasks, 'tasks')
@pytest.mark.django_db
def test_cleanup_successes(tasks_mock):
    # setup two objects. only one should be deleted.
    ghl = setup_data()
    setup_data()
    assert GithubLog.objects.count() == 2
    ghl.created = now() - timedelta(days=10)
    ghl.ack = True
    ghl.save()
    tasks.cleanup()
    assert GithubLog.objects.count() == 1
