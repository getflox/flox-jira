import re

from flox_jira.remote import with_jira
from floxcore.context import Flox


@with_jira
def create_project(flox: Flox, out, jira, **kwargs):
    """Create project"""
    project_key = re.sub(r"\W", "", flox.meta.id.upper())
    project = jira.project(project_key)
    
    if "id" in project:
        out.info("Using existing jira project")
        return

    data = dict(
        key=project_key,
        name=flox.meta.name,
        description=flox.meta.description,
        projectTypeKey="business",
        lead=flox.secrets.getone("jira_username")
    )
    project = jira.post("rest/api/2/project", data=data)

    if "errors" in project:
        out.error("Unable to create project with provided details")
        return

    out.success(f"Created new jira component {flox.meta.name}")


@with_jira
def create_component(flox: Flox, out, jira, **kwargs):
    """Create component"""
    components = jira.get_project_components(flox.settings.jira.component_project)
    if len(list(filter(lambda x: x["name"] == flox.meta.name, components))) > 0:
        out.info("Component already exists")
        return

    component = jira.create_component(dict(
        name=flox.meta.name,
        project=flox.settings.jira.component_project
    ))

    if "errors" in component:
        out.error(component["errors"].get("name"))
        return

    out.success(f"Created new jira component {flox.meta.name}")
