from functools import wraps

import click
from atlassian import Jira

from floxcore.context import Flox


def with_jira(f):
    @wraps(f)
    @click.pass_obj
    def wrapper(obj: Flox, *args, **kwargs):
        if not hasattr(with_jira, "client"):
            jira = Jira(
                url=obj.settings.jira.url,
                username=obj.secrets.getone("jira_username"),
                password=obj.secrets.getone("jira_api_token")
            )
            setattr(with_jira, "client", jira)

        kwargs["jira"] = getattr(with_jira, "client")
        return f(*args, **kwargs)

    return wrapper
