from functools import partial

import wit

import config
from state.errors import NoIntent, NoCommandFound
from utils.collectionutils import safe_get_value
from utils.mappingutils import generic_translator


class TransitionAdapter(object):
    registry = {

    }

    def __call__(self, ):
        pass


class Mapping(object):
    def __init__(self):
        self.strategy_and_mappings = []

    def add(self, strategy, mapping):
        self.strategy_and_mappings.append((strategy, mapping))
        return self

    def __iter__(self):
        return self.strategy_and_mappings.__iter__()


# mapping could be instance of Mapping or tuple/list
# list/tulple could be [("sourceKey1", "targetKey1"), ("sourceKey2", "targetKey2")]
# or [("sourceKey1","sourceKey2")], in this case targetKey = sourceKey
# when mapping is not Mapping instance , Mapping is instantiated with strategy = wit_entity_mapping
def wit_to_command(wit_message, cmd_class, mappings=None):
    cmd = cmd_class()

    def target_mapper(t_key, target, s_value):
        if t_key.startswith("$"):
            t_key = t_key[1:]
        cmd.set_attribute(t_key, s_value)

    if not mappings:
        for entity_name, entity_value in wit_message.get("entities").items():
            if not entity_name == "intent":
                generic_translator(entity_value, None, ("$[0].value", partial(target_mapper, entity_name)))

    else:
        if mappings and not isinstance(mappings, Mapping):
            mappings = Mapping().add(wit_entity_mapping, mappings)
        for strategy_mappings in mappings:
            strategy, mappings = strategy_mappings
            for mapping in mappings:
                if isinstance(mapping, (tuple, list)) and len(mapping) == 2:
                    s_key, t_key = mapping
                # expecting mapping  to be str
                elif isinstance(mapping, (str, unicode)):
                    s_key, t_key = mapping, mapping
                else:
                    raise AttributeError("illegal mapping {mapping}".format(mapping=mapping))

            # generic_translator(wit_message, None, ("$entities." + s_key + ".[0].value",
            #                                        partial(target_mapper, t_key)))
            strategy(wit_message, s_key, partial(target_mapper, t_key))

    cmd.name = safe_get_value(wit_message, "entities.intent.[0].value")

    return cmd


def wit_entity_mapping(wit_message, s_key, target_mapper):
    if s_key.startswith("$"):
        s_key = s_key[1:]
    generic_translator(wit_message, None, ("$entities."+s_key+".[0].value", target_mapper))


class WitToCommandAdapter(object):
    def __init__(self, config):
        self.config = config

    def adapt(self, witcommand):
        intent = safe_get_value(witcommand,"entities.intent.[0].value")
        if not intent:
            raise NoIntent("does not handle command")

        adapter = self.config.get(intent)
        if not adapter:
            raise NoCommandFound("no command found for intent %s " % intent)

        command = adapter(witcommand)
        return command


wit_client = wit.Wit(config.WIT_TOKEN)


def get_wit_command(msg):
    return wit_client.message(msg)


if __name__ == "__main__":
    witcommand = get_wit_command("show me jira abc-xyz")
    print witcommand
    v = safe_get_value(witcommand,"entities.intent.[0].value")
    cmd = WitToCommandAdapter.create_command(witcommand)
    print cmd
    print cmd.state
