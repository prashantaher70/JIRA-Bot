from werkzeug.local import LocalProxy, Local
from functools import partial


class User(object):
    def __init__(self):
        self.userid = None
        self.user = None
        self.command_flow = None

# An alternative approach
# userContext could have wrapped  local inside ; to make it conveneint for setting user related info
# class UserContext(object):
#     def __init__(self):
#         self._local = Local()
#
#     @property
#     def user(self):
#         self._local.user
#
#     @user.setter
#     def user(self,value):
#         self._local.user = value
#
# _user_context = UserContext()
# def get_user_context():
#     return _user_context.user


def get_usercontext(usercontext):
    try:
        return usercontext.user
    except AttributeError:
        usercontext.user = User()
    return usercontext.user

usercontext = LocalProxy(partial(get_usercontext, Local()))
