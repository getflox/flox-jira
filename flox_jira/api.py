import json
import re
import types

from click import ClickException
from jira import JIRA, JIRAError
from jira.resources import RemoteLink
from jira.utils import json_loads

from flox_jira.utils import format_issue

class JiraException(ClickException):
    pass


class Versions:
    def __init__(self, client, project):
        self.project = project
        self.client = client

    def list(self):
        return self.client.project_versions(self.project)

    def create(self, name):
        version = self.client.create_version(name, self.project)
        return self._bind(version)

    def version_url(self, version):
        if isinstance(version, str):
            version = self.find(version)

        return f"{self.client.base_url}/projects/{self.project}/versions/{version}"

    def find(self, version_name):
        version = filter(lambda x: x.name == version_name, self.list())

        return next(version, []) or None

    def _bind(self, version):
        version.url = types.MethodType(self.version_url, version)

        return version


class Issues:
    def __init__(self, client, project):
        self.project = project
        self.client = client

    def get(self, key):
        try:
            issue = self.client.issue(key)
            issue.formatted = types.MethodType(format_issue, issue)
            issue.url = types.MethodType(self.issue_url, issue)
            issue.assign_version = types.MethodType(self.assign_version, issue)
            issue.add_link = types.MethodType(self.add_link, issue)
            issue.links = types.MethodType(self.links, issue)

            return issue
        except JIRAError as e:
            raise JiraException(e.text)

    def issue_url(self, issue):
        return f"{self.client.base_url}/browse/{issue.key}"

    def add_link(self, issue, destination, link_type='branch preview'):
        url = self.client._get_url('issue/' + str(issue) + '/remotelink')

        data = {
            'relationship': link_type,
            'object': {
                'url': destination,
                'title': destination
            }
        }

        response = self.client._session.post(
            url, data=json.dumps(data)
        )

        return RemoteLink(
            self.client._options, self.client._session, raw=json_loads(response)
        )

    def links(self, issue, link_type='branch preview'):
        links = self.client.remote_links(issue)
        return filter(lambda x: x.relationship == link_type, links)

    def assign_version(self, issue, version):
        try:
            if len(issue.fields.fixVersions) > 0:
                print("Ignoring. Issue already assigned to version.")
                return

            issue.update(fields={
                'fixVersions': [{
                    'id': version.id
                }]
            })

            return version
        except JIRAError as e:
            raise JiraException(e.text)


class Integration:
    name = 'jira'

    def __init__(self, project_key, url, username, password, multiproject=True):
        options = {'server': str(url)}

        self.client = JIRA(
            options=options,
            basic_auth=(
                str(username),
                str(password)
            ),
        )
        self.client.base_url = url
        self.project_key = project_key
        self.project = self.client.project(project_key)
        self.multiproject = multiproject

        self.versions = Versions(self.client, self.project)
        self.issues = Issues(self.client, self.project)

    def parse_issues(self, messages):
        issues = set(
            map(
                lambda x: x.upper(),
                re.findall(self.project_key + r'\-\d+', messages, re.IGNORECASE)
            )
        )

        for issue_id in issues:
            try:
                issue = self.issues.get(issue_id)
                yield {
                    'key': issue.key,
                    'url': self.issues.issue_url(issue),
                    'type': issue.fields.issuetype,
                    'summary': issue.fields.summary
                }
            except:
                yield {'key': issue_id, 'url': self.issues.issue_url(issue_id)}
