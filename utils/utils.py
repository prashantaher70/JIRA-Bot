import uuid


class OmniWheelException(Exception):
    pass


class AuthenticationException(Exception):
    pass


class InvalidCommandAttribue(Exception):
    pass


def generate_user_id():
    return uuid.uuid4()