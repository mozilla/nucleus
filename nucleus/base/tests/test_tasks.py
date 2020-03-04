from unittest.mock import patch

from django.apps import apps
from django.utils.timezone import now

import pytest
from github import UnknownObjectException

from nucleus.base import tasks


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


def setup_data():
    model = apps.get_model('rna.release')
    obj = model.objects.create(
        product='Firefox',
        channel='Nightly',
        version='73.0a1',
        release_date=now(),
    )
    user_model = apps.get_model('auth.user')
    user = user_model.objects.create(
        username='dude',
        email='dude@example.com',
        first_name='The',
        last_name='Dude',
    )
    return obj, user


@patch.object(tasks, 'github')
@pytest.mark.django_db
def test_save_to_github_update(gh_mock):
    obj, user = setup_data()
    repo = gh_mock.get_repo()

    # with file already in github
    ghf = repo.get_contents()
    ghf.decoded_content = '{}'
    tasks.save_to_github('rna.release', obj.pk, user.pk, 'test')
    repo.get_contents.assert_called_with('releases/firefox-73.0a1-nightly.json', ref='test')
    gh_mock.get_author.assert_called_with(user)
    repo.update_file.assert_called_with('releases/firefox-73.0a1-nightly.json',
                                        'Update releases/firefox-73.0a1-nightly.json',
                                        obj.to_json(),
                                        ghf.sha,
                                        branch='test',
                                        author=gh_mock.get_author())


@patch.object(tasks, 'github')
@pytest.mark.django_db
def test_save_to_github_skip_update(gh_mock):
    """Should skip updating or creating if the data is the same"""
    obj, user = setup_data()
    repo = gh_mock.get_repo()

    # with file already in github
    orig_json = obj.to_json()
    ghf = repo.get_contents()
    ghf.decoded_content = orig_json
    obj.save()  # update modified so that they're different
    new_json = obj.to_json()
    # should have different modified times
    assert new_json != orig_json
    tasks.save_to_github('rna.release', obj.pk, user.pk, 'test')
    repo.get_contents.assert_called_with('releases/firefox-73.0a1-nightly.json', ref='test')
    gh_mock.get_author.assert_called_with(user)
    repo.update_file.assert_not_called()
    repo.create_file.assert_not_called()


@patch.object(tasks, 'github')
@pytest.mark.django_db
def test_save_to_github_create(gh_mock):
    obj, user = setup_data()
    repo = gh_mock.get_repo()

    # with no file already in github
    repo.get_contents.side_effect = UnknownObjectException('failed', 'missing')
    tasks.save_to_github('rna.release', obj.pk, user.pk, 'test')
    repo.get_contents.assert_called_with('releases/firefox-73.0a1-nightly.json', ref='test')
    gh_mock.get_author.assert_called_with(user)
    repo.create_file.assert_called_with('releases/firefox-73.0a1-nightly.json',
                                        'Create releases/firefox-73.0a1-nightly.json',
                                        obj.to_json(),
                                        branch='test',
                                        author=gh_mock.get_author())
