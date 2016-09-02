import logging
from functools import wraps

from httplib2 import ServerNotFoundError
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.namespace import BaseNamespace

import jira_service
from apis import get_jira
from apis_wrap import OmniWheelException
from auth import AuthenticationException
from auth import start_auth, continue_auth, sync_self_user, create_org
from context import usercontext
from mongouserorgcollection import get_user_from_db_or_error
from utils.redis_utils import listen_redis
from notifications import process_event
import gevent
from commandconfig.commandflow import CommandFlow
from utils.utils import InvalidCommandAttribue
from state.errors import NoCommandFound, NoIntent


def exception_handler(f):
    def f_wrap(*args, **kwargs):
        response = {}
        try:
            logging.debug("args are {args}".format(args=args))
            response = f(*args, **kwargs)
            if not response:
                response = {}

        except AuthenticationException as e:
            response["error"] = True
            response["errorCode"] = 401
            response["errorMessage"] = str(e)

        except OmniWheelException as e:
            response["error"] = True
            response["errorCode"] = 409
            response["errorMessage"] = str(e)

        except ServerNotFoundError:
            response["error"] = True
            response["errorCode"] = 503
            response["errorMessage"] = "Unable to connect to JIRA service"

        except InvalidCommandAttribue as e:
            response["error"] = True
            response["errorCode"] = 400
            response["errorMessage"] = str(e)

        except (NoIntent, NoCommandFound) as e:
            response["error"] = True
            response["errorCode"] = 404
            response["errorMessage"] = str(e)

        except Exception as e:
            response["error"] = True
            response["errorCode"] = 500
            response["errorMessage"] = str(e)
            logging.exception("message")
        return response
    return f_wrap


def on_error(error_event_name):
    def _wrapper(f):
        def inner(self, *args, **kwargs):
            print "obj"
            print self
            print args

            response = exception_handler(f)(self, *args, **kwargs)
            if response and isinstance(response, dict) and response.get("error"):
                self.emit(error_event_name, response)
            return response
        return inner
    return _wrapper


def session_filter(f):
    @wraps(f)
    def f_wrap(*args, **kwargs):
        if usercontext.userid:
            logging.info("userid" + usercontext.userid)
        else:
            raise AuthenticationException("No userid found in session")

        return f(*args, **kwargs)
    return f_wrap


class OmniWheelAuthNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

    def initialize(self):
        self.log("Socketio session started")
        self.running = False

    def log(self, message):
        logging.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_AUTH_set_user_context(self, userid):
        if userid:
            try:
                user = get_user_from_db_or_error(userid)
                usercontext.userid = userid
                usercontext.user = user
                logging.info("setting userId in session, userId:  " + userid)

                self.spawn(self.notification_job, userid)
            except AuthenticationException:
                logging.info("User not found. Not setting user context")
                pass
        self.emit('set_user_context_response', {})


    def on_AUTH_start_auth(self, data):
        @exception_handler
        def inner():
            res = {}
            userId, authUrl = start_auth(data['orgName'], data.get('userId'), data.get('configuring'))
            res["data"] = {}
            res["data"]["userId"] = userId
            res["data"]["authUrl"] = authUrl
            res["data"]["orgName"] = data['orgName']
            return res

        response = inner()
        self.emit("AUTH_start_auth_response", response)
        return True

    def on_AUTH_continue_auth(self, data):
        @exception_handler
        def inner():
            continue_auth(data['userId'])

        response = inner()

        self.emit("AUTH_continue_auth_response", response)
        return True

    def on_AUTH_sync_user_set_webhook(self, data):
        @exception_handler
        def inner():
            self.on_AUTH_set_user_context(data["userId"])
            sync_self_user()
            logging.debug("Refreshing user context as update has happened on user")
            self.on_AUTH_set_user_context(data["userId"])
            jira_service.register_webhook_if_not_present()

        response = inner()
        self.emit("AUTH_sync_user_set_webhook_response", response)
        return True

    def on_AUTH_create_org(self, data):

        @exception_handler
        def inner():
            create_org(data['orgName'], data['orgJiraEndpoint'])

        response = inner()
        self.emit("AUTH_create_org_response", response)
        return True

    def on_AUTH_get_jira(self, data):
        if usercontext.userid:
            logging.info("userid" + usercontext.userid)
        else:
            logging.info("did not find userid in context")

        @exception_handler
        def inner():
            res = {
                'data': get_jira(data['issue'])
            }
            return res
        logging.info("making jira call ")
        response = inner()
        self.emit("AUTH_get_jira_response", response)
        return True

    @on_error("command_response")
    def on_command_request(self, data):
        # command_str = data.get("command")
        command_flow = create_command_flow(self, data)
        usercontext.command_flow = command_flow
        command_flow.initcommand()
    # on_command_request = on_error("command_response")(on_command_request)

    @on_error("command_response")
    def on_ask_response(self, data):
        # assuming data to be {"a":"A", "b":"B"}
        try:
            command_flow = usercontext.command_flow
            command_flow.add_attributes(data)
        except AttributeError as e:
            raise InvalidCommandAttribue("wrong attribues {data} ".format(data = data))

    def notification_job(self, userid):
        if self.running:
            return

        self.running = True
        logging.debug("Notification job started")

        notifications = listen_redis(str(userid))
        for notification in notifications:
            p_event = process_event(userid, notification)
            self.emit("notification", p_event)

    def on_load_notifications(self, data):
        @exception_handler
        def inner():
            if not usercontext.userid:
                raise AuthenticationException('No user ID in context')
            res = {
                'data': jira_service.get_notifications_from_db()
            }
            return res

        response = inner()
        self.emit("load_notifications_response", response)


def create_command_flow(connection_obj, command_str):

    def on_command_complete(data):
        connection_obj.emit("command_response", data)

    def on_incomplete_command(data):
        connection_obj.emit("ask", data)

    def _on_error(e):
        raise e

    command_flow = CommandFlow(command_str)
    command_flow.complete = on_command_complete
    command_flow.incomplete = on_incomplete_command
    command_flow.error = _on_error

    return command_flow
