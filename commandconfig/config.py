from functools import partial

from apis import apis
from state import witutils
from state.command import Command
from state.jiraadapter import jira_target_function_and_mapping


class OpenJira(Command):
    attrs = ["issueName"]
    response_type = "jira"


class ShowJira(Command):
    attrs = ["issueNumber"]
    response_type = "jira"


class ShowComments(Command):
    attrs = ["issueNumber"]
    response_type = "comment"


intent_to_command = {
    # "showjira" : partial(witutils.cmd_and_mapper, cmd_class = ShowJira)
    "showjira" : partial(witutils.wit_to_command, cmd_class=ShowJira, mappings=["$issueNumber"]),
    "showcomment" : partial(witutils.wit_to_command, cmd_class=ShowComments, mappings=["$issueNumber"])
}

# maps args to list
getjira = partial(jira_target_function_and_mapping,
                  t_function=apis.get_jira,
                  args_mappings=["$issueNumber"])
cmdname_to_jiracmd = {
    "showjira": partial(jira_target_function_and_mapping,
                        t_function=apis.get_jira,
                        args_mappings=["$issueNumber"]),
    "showcomment": partial(jira_target_function_and_mapping,
                           t_function=apis.get_jira,
                           args_mappings=["$issueNumber"], response_f = lambda r : {"comment": r["fields"]["comment"]})
}


