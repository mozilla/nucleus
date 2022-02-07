import json
from copy import deepcopy
from datetime import timedelta
from logging import getLogger

from django.utils.timezone import now

from github import UnknownObjectException
from spinach import Tasks

from nucleus.base import github

log = getLogger(__name__)
tasks = Tasks(max_retries=8)
MAX_FAILS = 5


@tasks.task(name="nucleus:cleanup", periodicity=timedelta(hours=1))
def cleanup():
    from .models import GithubLog  # avoid circular import

    # requeue any that are unacknowledged after an hour
    unacked = GithubLog.objects.filter(ack=False, fail_count__lt=MAX_FAILS, created__lt=now() - timedelta(hours=1))
    count = 0
    for ghl in unacked:
        ghl.fail_count += 1
        ghl.save()
        tasks.schedule(save_to_github, ghl.pk)
        count += 1

    log.info(f"scheduled {count} GithubLog entries for trying again")

    # delete acknowledged entries after a week
    acked = GithubLog.objects.filter(ack=True, created__lt=now() - timedelta(weeks=1))
    num_deleted, _ = acked.delete()
    log.info(f"deleted {num_deleted} GithubLog entries")


@tasks.task(name="nucleus:save_to_github")
def save_to_github(ghl_id):
    from .models import GithubLog  # avoid circular import

    ghl = GithubLog.objects.get(pk=ghl_id)
    log.debug(f"save_to_github: {ghl}")
    obj = ghl.content_object
    file_path = obj.json_file_path
    content = obj.to_json()
    repo = github.get_repo()
    try:
        ghf = repo.get_contents(file_path, ref=ghl.branch)
        action = "Update"
    except UnknownObjectException:
        ghf = None
        action = "Create"

    message = f"{action} {file_path}"
    kwargs = {"branch": ghl.branch}
    if ghl.author:
        kwargs["author"] = github.get_author(ghl.author)

    if ghf:
        current_data = json.loads(ghf.decoded_content)
        if data_matches(current_data, obj.to_dict()):
            log.info(f"{file_path} data matches. not updating file.")
            return

        resp = repo.update_file(file_path, message, content, ghf.sha, **kwargs)
    else:
        resp = repo.create_file(file_path, message, content, **kwargs)

    log.info(f"committed to github: {resp['commit'].sha}")
    log.info(message)
    ghl.ack = True
    ghl.save()


def data_matches(data1, data2):
    """Return True if the data in both args is the same ignoring any "modified" keys."""
    return remove_modified(data1) == remove_modified(data2)


def remove_modified(data):
    """Recursively remove any "modified" key from the dict"""
    data = deepcopy(data)
    for key in list(data.keys()):
        if key == "modified":
            del data[key]
        elif isinstance(data[key], (list, tuple)):
            for i, item in enumerate(data[key]):
                if isinstance(item, dict):
                    data[key][i] = remove_modified(item)
        elif isinstance(data[key], dict):
            data[key] = remove_modified(data[key])

    return data
