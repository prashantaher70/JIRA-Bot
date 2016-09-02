# Command Flow reacts on
# incomplete , complete , error
#
from adapter import adapter
from state.usercontext import INCOMPLETE, COMPLETE
import traceback
from state.witutils import get_wit_command
import logging


class CommandFlow(object):
    def __init__(self, commandstr, command_adapter=adapter ):
        self.commandstr = commandstr
        self.command_adapter = command_adapter
        self.cmd = None
        # self.initcommand()

    def __setter__(self, name, value):
        setattr(self, name, value)
        return self

    incomplete = property(fget=lambda s: s._incomplete, fset = lambda s,v : s.__setter__("_incomplete",v))
    complete = property(fget = lambda s:s._complete, fset = lambda s,v: s.__setter__("_complete",v))
    error = property(fget = lambda s:s._error, fset = lambda s,v: s.__setter__("_error",v))

    def error_handler(f):
        def _handler(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                return self.error(e)
        return _handler


    @error_handler
    def initcommand(self):
        logging.debug("cmd_str received is " + self.commandstr)
        wit_str = get_wit_command(self.commandstr)
        logging.debug("wit response received {wit_r}".format(wit_r=wit_str))
        cmd = self.command_adapter.get_cmd_from_wit(wit_str)
        logging.debug ("bot command name is " + cmd.name)
        self.cmd = cmd
        self._react_on_state()

    def _react_on_state(self):
        cmd = self.cmd
        if cmd.state == INCOMPLETE:
            return self.incomplete(cmd.incomplete_attrs)

        if cmd.state == COMPLETE:
            jiracmd = self.command_adapter.get_jiracmd_from_cmd(cmd)
            jira_response = jiracmd()
            jira_response["type"] = cmd.response_type
            return self.complete(jira_response)

    @error_handler
    def add_attributes(self, _dict):
        for name, value in _dict.items():
            self.cmd.set_attribute(name,value)
        self._react_on_state()

    @error_handler
    def add_command_attribute(self, name, value):
        self.cmd.set_attribute(name, value)
        self._react_on_state()

if __name__ == "__main__":
    c = CommandFlow("show jira")
    c.error = lambda e:e
    c.incomplete = lambda m : m
    c.complete = lambda m:m

    c.initcommand()
    c.add_command_attribute("issueNumber","abc-xyz")