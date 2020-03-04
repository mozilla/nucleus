from django.conf import settings

from github import Github, InputGitAuthor


GITHUB_CLIENT = None


def get_client():
    global GITHUB_CLIENT
    if GITHUB_CLIENT is not None:
        return GITHUB_CLIENT

    if settings.GITHUB_ACCESS_TOKEN:
        GITHUB_CLIENT = Github(settings.GITHUB_ACCESS_TOKEN)

    return GITHUB_CLIENT


def get_repo():
    client = get_client()
    if not client:
        return

    return client.get_repo(settings.GITHUB_OUTPUT_REPO)


def get_author(user):
    name = user.get_full_name() or 'Nucleus User'
    return InputGitAuthor(name, user.email)


def repo_url():
    return f'https://github.com/{settings.GITHUB_OUTPUT_REPO}'
