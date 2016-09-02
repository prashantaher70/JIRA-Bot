import logging
INCOMPLETE = "INCOMPLETE"
COMPLETE = "COMPLETE"
#from command import Command, AttributeNode



command_registry = dict()

# to be defined inside command
attribute_registry = dict()
rootlogger = logging.getLogger()
rootlogger.setLevel("DEBUG")


# example command


class Request(object):
    # TODO - may change request type on "type"
    def __init__(self, request_type, json):
        self.type = request_type
        self.__raw = json

    def get_command(self):
        if self.request_type == "COMMAND":
            return self.__raw

    @property
    def attributes(self):
        if self.request_type == "INPUT":
            return self.json.items()


class Response(object):
    def __init__(self, request_type , value):
        self.type = request_type
        self._raw = value


class UserContext(object):
    def __init__(self):
        self.command = None
        self.required = ["oauthtoken"]

    def process(self, request):
        if request.type == "command":
            self.command = find_command(request.text)
        if request.type == "input":
            self.command.setattrs(request.attributes)

        if self.command.state == INCOMPLETE:
            #create response with Ask
            pass
        else:
            # ask jira to complete command
            pass
        return Response()


def find_command(text):
    # return Command()
    pass


__commands_registry__ = dict()


# if __name__ == "__main__":
#     # show_jira = ShowJira()
#     # print show_jira.state
#     # show_jira.set_attribute("issueName", "SPH-123")
#     # show_jira.set_attribute("name","JIRA123")
#     # print show_jira.state
#     # print show_jira.incomplete_attrs
#     # show_jira.set_attribute("issueType", "Test")
#     # assert show_jira.state == INCOMPLETE
#     # show_jira.set_attribute("resolution","DONE")
#     # assert  show_jira.state == COMPLETE
#     # assert show_jira.incomplete_attrs == []
#
#     class OpenAttr(AttributeNode):
#         attrs = ["issueName","name"]
#
#     class Open(Command):
#         attrs = [("open", OpenAttr)]
#
#     openJira = Open()
#     print openJira.state
#     print openJira.incomplete_attrs
#     openJira.set_attribute("open.issueName","SPH-43")
#     print openJira.state
#     print openJira.incomplete_attrs
#     openJira.set_attribute("open.name", "SPH-43")
#     print openJira.incomplete_attrs
#     print openJira.state


