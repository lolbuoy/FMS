from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import logging

app = Flask(__name__)
app.config.from_object("config.Config")
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes
from routes import *
from socket_manager import *

# START POLLING REDIS
from polling import poll_redis


def start_poll_redis():
    with app.app_context():
        REDIS_POLL_INTERVAL = app.config["REDIS_POLL_INTERVAL"]

        poll_redis(__name__, REDIS_POLL_INTERVAL)


if __name__ == "__main__":

    # START ANOTHER THREAD WITH POLL FUNCTION
    server_process = socketio.start_background_task(target=start_poll_redis)

    # START WEBSOCKET + FLASK APP
    socketio.run(app, host="100.75.51.60", port=4010, allow_unsafe_werkzeug=True)
