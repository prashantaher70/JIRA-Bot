import config
from state.witutils import WitToCommandAdapter
from state.jiraadapter import JiraAdapter


class Adapter(object):
    def __init__(self, wit_to_cmd_adapter=WitToCommandAdapter(config.intent_to_command),
                 cmd_to_jiracmd_adapter=JiraAdapter(config.cmdname_to_jiracmd)):
        self.wit_to_cmd_adapter = wit_to_cmd_adapter
        self.cmd_to_jiracmd_adapter = cmd_to_jiracmd_adapter

    def get_cmd_from_wit(self, witmessage):
        return self.wit_to_cmd_adapter.adapt(witmessage)

    def get_jiracmd_from_cmd(self, cmd):
        return self.cmd_to_jiracmd_adapter.adapt(cmd)


adapter = Adapter()
