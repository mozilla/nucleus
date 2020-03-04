import json
from copy import deepcopy
from logging import getLogger

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User

from github import UnknownObjectException
from spinach import Tasks

from nucleus.base import github


log = getLogger(__name__)
tasks = Tasks(max_retries=8)


@tasks.task(name='nucleus:save_to_github')
def save_to_github(model_label, instance_id, author_id=None, branch=None):
    log.debug(f'save_to_github, {model_label}, {instance_id}, {author_id}, {branch}')
    branch = branch or settings.GITHUB_OUTPUT_BRANCH
    model = apps.get_model(model_label)
    obj = model.objects.get(pk=instance_id)
    user = User.objects.get(pk=author_id)
    author = github.get_author(user)
    file_path = obj.json_file_path
    content = obj.to_json()
    repo = github.get_repo()
    try:
        ghf = repo.get_contents(file_path, ref=branch)
        action = 'Update'
    except UnknownObjectException:
        ghf = None
        action = 'Create'

    message = f'{action} {file_path}'
    if ghf:
        current_data = json.loads(ghf.decoded_content)
        if data_matches(current_data, obj.to_dict()):
            log.info(f'{file_path} data matches. not updating file.')
            return

        resp = repo.update_file(file_path,
                                message,
                                content,
                                ghf.sha,
                                branch=branch,
                                author=author)
    else:
        resp = repo.create_file(file_path,
                                message,
                                content,
                                branch=branch,
                                author=author)

    log.info(f"committed to github: {resp['commit'].sha}")
    log.info(message)


def data_matches(data1, data2):
    """Return True if the data in both args is the same ignoring any "modified" keys."""
    return remove_modified(data1) == remove_modified(data2)


def remove_modified(data):
    """Recursively remove any "modified" key from the dict"""
    data = deepcopy(data)
    for key in list(data.keys()):
        if key == 'modified':
            del data[key]
        elif isinstance(data[key], (list, tuple)):
            for i, item in enumerate(data[key]):
                if isinstance(item, dict):
                    data[key][i] = remove_modified(item)
        elif isinstance(data[key], dict):
            data[key] = remove_modified(data[key])

    return data
