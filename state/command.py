from state.usercontext import INCOMPLETE, COMPLETE


class Command(object):
    # attrs = [("issueNumber",str), ("issue", IssueAttr)]
    # attrs = ["issueNumber", ("issue",IssueAttr)]
    attrs = None

    def __init__(self, name=None):
        self._state = INCOMPLETE
        self.attrs_registry = {}
        # to maintain order of attrs
        self.attr_names = []
        if name:
            self._name = name
        for name_cls in self.attrs:
            if isinstance(name_cls, str):
                self.attrs_registry[name_cls] = str
                self.attr_names.append(name_cls)
                # todo - str could be wrapped in leaf
            else:
                attr_name, attr_cls = name_cls
                self.attrs_registry[attr_name] = attr_cls
                self.attr_names.append(attr_name)
                self.__dict__[attr_name] = attr_cls()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def incomplete_attrs(self):

        if self.state == COMPLETE:
            return []
        incomplete = []
        first_incomplete_attr_node = None
        for attr_name in self.attr_names:
            # todo first check for  leaf (with  str class)
            attr = self.__dict__.get(attr_name)
            if not attr:
                incomplete.append(attr_name)
            elif not first_incomplete_attr_node and attr and not self.attrs_registry[attr_name] == str and attr.state == INCOMPLETE:
                first_incomplete_attr_node = attr
        if not incomplete and first_incomplete_attr_node:
            return first_incomplete_attr_node.incomplete_attrs
        return incomplete

    def set_attributes(self, items):
        for name, value in items:
                self.set_attribute(name,value)

    def set_attribute(self, name, value):
        sep = "."
        if sep in name:
            first, rest = name.split(".", 1)
            attr = self.__dict__.get(first)
            if not attr:
                raise AttributeError("no attribute of name %s in command %s"%(name, self.__class__.__name__))
            attr.set_attribute(rest, value)
        else:
            if name in self.attrs:
                self.__dict__[name] = value
            else:
                raise AttributeError("no attribute of name %s in command %s"%(name,self.__class__.__name__))

    def get_attr(self, name):
        return self.__dict__.get(name,None)

    def initialize_attr(self,name):
        pass

    @property
    def state(self):
        if self._state == COMPLETE:
            return self._state
        #TODO - move to

        for attr_name in self.attr_names:
            attr = self.__dict__.get(attr_name, None)
            if not attr:
                return INCOMPLETE
            elif attr and isinstance(attr, AttributeNode) and attr.state == INCOMPLETE:
                return INCOMPLETE
        self._state = COMPLETE
        return self._state


class AttributeNode(Command):
    def __init__(self):
        Command.__init__(self)


class OpenJira(Command):
    attrs = ["issueName"]


class ShowJira(Command):
    attrs = ["issueNumber"]