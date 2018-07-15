from schema import Optional

from flox_jira.api import Integration


def config():
    return {
        'project_key': str,
        Optional('url'): str,
        Optional('username'): str,
        Optional('password'): str,
    }


def services(container, config):
    container.registry(
        Integration(config.project_key, config.url, config.username, config.password),
        ['issue_tracker']
    )
