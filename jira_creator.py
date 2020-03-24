#!/usr/bin/env python3
from configparser import RawConfigParser
from jira import JIRA, exceptions


# creds in atlassian_api.py
def jira_api_config():
    atlassian_config = RawConfigParser()
    try:
        atlassian_config.read("atlassian.cfg")
    except FileNotFoundError:
        print("missing atlassian config file")
        exit(1)

    try:
        api_user = atlassian_config.get("atlassian", "api_user")
        api_token = atlassian_config.get("atlassian", "api_token")

        server = atlassian_config.get("atlassian", "server")
    except:
        print("error reading atlassian API config")
        exit(1)


    # By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK
    # (see https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK for details).
    # Override this with the options parameter.
    options = {'server': server}

    #api_user = atlassian_api.api_user.split('@')[0]
    return JIRA(options, basic_auth=(api_user, api_token))


# components - list of dicts
# labels - list
# attachments - list of filenames/paths
def create_jira_ticket(title, content, project, issuetype, components=[], labels=[], attachments=[]):
    jira = jira_api_config()
    JIRA_CHAR_LIMIT = 32767

    # Issue creation
    issue_dict = {
        'project': {'key': project},
        'summary': title,
        'issuetype': {'name': issuetype}, # Hunt issue type,
        'labels': labels,
        'components': components,
        }
    new_issue = jira.create_issue(fields=issue_dict)

    # Add specified content to new issue
    # If JIRA error such as content > 32767 chars, pass
    try:
        new_issue.update(description=content)
    except exceptions.JIRAError as e:
        print("Error adding text size %d to issue: " % len(content), repr(e))

        # Add truncated text and label
        new_issue.update(description=content[:JIRA_CHAR_LIMIT])
        new_issue.fields.labels.append("Truncated")
        new_issue.update(fields={"labels": new_issue.fields.labels})

        for attachment in attachments:
            try:
                jira.add_attachment(issue=new_issue, attachment=attachment)
            except (FileNotFoundError, PermissionError) as e:
                print(e)

    return new_issue
