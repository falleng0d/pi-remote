import asyncio
import logging
import os

import flask
from werkzeug import exceptions

import log
import json_response
import socket_api

host = os.environ.get('HOST', '0.0.0.0')
port = int(os.environ.get('PORT', 5000))
debug = 'DEBUG' in os.environ
use_reloader = os.environ.get('USE_RELOADER', '0') == '1'

root_logger = log.create_root_logger(flask.logging.default_handler)
if debug:
    root_logger.setLevel(logging.DEBUG)
else:
    root_logger.setLevel(logging.INFO)
    # Socket.io logs are too chatty at INFO level.
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.info('Starting app')

app = flask.Flask(__name__)
app.config.update()
settings_file = os.environ.get('SETTINGS_FILE', '../settings.cfg')
cwd = os.path.dirname(os.path.realpath(__file__))
settings_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             settings_file)
app.config.from_pyfile(settings_file)


@app.errorhandler(Exception)
def handle_error(e):
    logger.exception(e)
    code = 500
    if isinstance(e, exceptions.HTTPException):
        code = e.code
    return json_response.error(e), code


async def main():
    socketio = socket_api.socketio
    socketio.init_app(app)
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=use_reloader,
        log_output=debug,
    )


if __name__ == '__main__':
    asyncio.run(main())
