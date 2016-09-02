def get_value(dict_, prop, splitter=lambda x: x.split("."), default_factory=None):
    def _value(_dict_, p):

        if not _dict_:
            if default_factory:
                return default_factory()
            raise TypeError("can not get property on NoneType")
        if not hasattr(_dict_, "__getitem__"):
            if default_factory:
                return default_factory()
            raise AttributeError("does not have attr __getitem__")
        if p.startswith("[") and p.endswith("]"):
            p = int(p[1:-1])
        try:
            return _dict_.__getitem__(p)
        except KeyError as e:
            if default_factory:
                return default_factory()
            raise e

    return reduce(_value, splitter(prop), dict_)


def safe_get_value(dict_, prop, splitter=lambda x: x.split(".")):
    return get_value(dict_, prop, splitter=splitter, default_factory=lambda: None)


def is_iterable(it):
    return hasattr(it, "__iter__") or hasattr(it, "next")


def add_value(dict_, prop, value):
    target_keys = prop.split(".")
    node = dict_
    for target_key in target_keys[:-1]:
        target_value = node.get(target_key)
        if target_value:
            node = target_value
        else:
            target_value = {}
            node[target_key] = target_value
            node = target_value

    node[target_keys[-1]] = value
    return dict_


def flatten(xs):
    new_result = []
    if is_iterable(xs) and not isinstance(xs, dict):
        for x in xs:
            if is_iterable(x) and not isinstance(x, dict):
                new_result.extend(flatten(list(x)))
            else:
                new_result.append(x)
    else:
        return xs
    return new_result
