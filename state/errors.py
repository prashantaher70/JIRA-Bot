class CommandError(Exception):
    pass


class NoIntent(CommandError):
    pass


class NoCommandFound(CommandError):
    pass