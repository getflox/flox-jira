def format_issue(issue):
    return f"[{issue.key}]({issue.url()}) - {issue.fields.issuetype} - {issue.fields.summary}"
