from utils import mappingutils
from utils.collectionutils import safe_get_value
from witutils import get_wit_command, WitToCommandAdapter
import logging

def jira_target_function_and_mapping(s_cmd, t_function,  args_mappings, http_method="GET", body_mappings=None,
                                     response_f=None):
    source = s_cmd.__dict__
    t_kwargs = {}
    t_args = []

    def arg_target_mapper(target, source_value):
        target.append(source_value)

    for mapping in args_mappings:
        # mappingutils.generic_translator(source, t_kwargs, mapping)
        mappingutils.generic_translator(source, t_args, (mapping, arg_target_mapper))
    t_kwargs["method"] = http_method
    body = {}
    if body_mappings:
        for body_mapping in body_mappings:
            mappingutils.generic_translator(source, body, body_mapping)
    t_kwargs["body"] = body
    if response_f:
        t_kwargs["response_f"] = response_f
    return JiraCommand(t_function, *t_args, **t_kwargs)


class JiraAdapter(object):
    def __init__(self, config):
        self.config = config

    def adapt(self, src_cmd):
        name = src_cmd.name
        logging.info("cmd name is " + name)
        adapter = self.config.get(name)
        if not adapter:
            raise ValueError("no Jira adapter registered  for command  %s "% name)
        return adapter(src_cmd)


class JiraCommand(object):

    def __init__(self, target_function, *t_args, **t_kwargs):
        if not t_kwargs["method"]:
            t_kwargs["method"] = "GET"
        self.target_function = target_function
        self.t_args = t_args
        self.t_kwargs = t_kwargs

    def add_user_id(self, user_id):
        self.t_kwargs["user_id"] = user_id

    def __call__(self):
        response_f = self.t_kwargs.pop("response_f", None)
        logging.info("calling jira with args {args}".format(args=self.t_args))
        response = self.target_function(*self.t_args, **self.t_kwargs)
        if response_f:
            return response_f(response)
        else:
            return response


if __name__ == "__main__":
    witcommand = get_wit_command("show me jira abc-xyz")
    print witcommand
    v = safe_get_value(witcommand,"entities.intent.[0].value")
    cmd = WitToCommandAdapter.create_command(witcommand)
    print cmd
    print cmd.state
    j_cmd = JiraAdapter.get_command(cmd, "abc")
    print j_cmd.target_function
    print j_cmd.t_kwargs