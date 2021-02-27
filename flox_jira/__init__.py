from typing import Tuple

from flox_jira.project import create_project, create_component
from floxcore.command import Stage
from floxcore.config import Configuration, ParamDefinition
from floxcore.context import Flox
from floxcore.plugin import Plugin


class JiraConfiguration(Configuration):
    def parameters(self):
        return (
            ParamDefinition("url", "Jira Instance URL"),
            ParamDefinition("create_project", "Create Jira project for each flox project", boolean=True),
            ParamDefinition("create_component", "Create Jira component for each flox project", boolean=True),
            ParamDefinition("component_project", "Jira project Id under which component should be created",
                            depends_on="create_component"),
        )

    def secrets(self) -> Tuple[ParamDefinition, ...]:
        return (
            ParamDefinition("username", "Username"),
            ParamDefinition("api_token", "API Token"),
        )

    def schema(self):
        pass


class JiraPlugin(Plugin):
    def configuration(self):
        return JiraConfiguration()

    def handle_project(self, flox: Flox):
        return (
            Stage(create_project, require=["jira.create_project"]),
            Stage(create_component, require=["jira.create_component"]),
        )


def plugin():
    return JiraPlugin()
