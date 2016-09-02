from app import app
from gevent import monkey
from socketio.server import SocketIOServer
from gevent import monkey
from socketio import socketio_manage
from apis.auth_namespace import OmniWheelAuthNamespace
from flask import request, Response
import loggingutils
monkey.patch_all()

loggingutils.initialize_logger()

@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'': OmniWheelAuthNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()

PORT = 5000

if __name__ == '__main__':
    print 'Listening on http://127.0.0.1:%s and on port 10843 (flash policy server)' % PORT
    SocketIOServer(('', PORT), app, resource="socket.io").serve_forever()