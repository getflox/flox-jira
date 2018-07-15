import click


@click.group()
@click.pass_obj
def jira(flox):
    """Jira tools for flox"""
