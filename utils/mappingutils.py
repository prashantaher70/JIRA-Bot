from collectionutils import safe_get_value, add_value


def generic_translator(source, target, translator):
    # translator could be a callable or
    # OR:
    # translator could be a tuple or list
    # 1.has function or key to extract value from source
    # 2.optional  a processor to process source value
    # 3. target function or key to set value in target
    # OR:
    # 1. has function or key to extract value from source
    # 2. target function or key to set value in target
    if callable(translator):
        return translator(source, target)
    if not isinstance(translator,(tuple,list)):
        raise TypeError("translator should be either callable or list or tuple")
    if not len(translator) in (2, 3):
        raise TypeError("length should be either 2 or 3")

    source_f, processor, target_f = None, None, None

    if len(translator) == 2:
        source_f, target_f = translator
    if len(translator) == 3:
        source_f, processor, target_f = translator

    def _source_result():
        try:
            if callable(source_f):
                return source_f(source)
            elif isinstance(source_f, str):
                if source_f.startswith("$"):
                    return safe_get_value(source, source_f[1:])
                else:
                    return source_f
            else:
                raise TypeError("can not handle source_extractor of type {t}".format(t=type(source_f)))
        except KeyError as e:
            return None

    def _processor(s_value):
        if not callable(processor):
            raise TypeError("processor should be callable")
        return processor(s_value)

    def _target(value):
        if callable(target_f):
            target_f(target, value)
        elif isinstance(target_f, str):
            if target_f.startswith("$"):
                add_value(target, target_f[1:], value)
            else:
                add_value(target, target_f, value)
        else:
            TypeError("can not handle target_f of type {t}".format(t=type(target_f)))

    source_value = _source_result()

    if processor:
        source_value = _processor(source_value)

    _target(source_value)
