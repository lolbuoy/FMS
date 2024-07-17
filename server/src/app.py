# import eventlet
# eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
import threading

app = Flask(__name__)
app.config.from_object("config.Config")
socketio = SocketIO(app, cors_allowed_origins="*")


def send_event(data, type="redis_update"):
    print(data)
    socketio.emit(type, data, include_self=True)


CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes
from routes import *
from socket_manager import *
from mqtt_manager import start_mqtt_manager, start_mqtt_manager_forever

# START POLLING REDIS
from polling import poll_redis


def start_poll_redis():
    with app.app_context():
        REDIS_POLL_INTERVAL = app.config["REDIS_POLL_INTERVAL"]

        poll_redis(__name__, REDIS_POLL_INTERVAL)


def start_mqtt():
    # START SUBSCRIPTION TO MESSAGES

    # with app.app_context():
    print(threading.get_ident())
    start_mqtt_manager()


if __name__ == "__main__":
    print(Config.MQTT_BROKER_URL)
    print(app.config["MQTT_BROKER_URL"])

    # # MQTT SUPPORT
    # with app.app_context():
    #     from mqtt_manager import *

    # START ANOTHER THREAD WITH POLL FUNCTION
    server_process = socketio.start_background_task(target=start_poll_redis)
    mqtt_process = socketio.start_background_task(target=start_mqtt)

    # START WEBSOCKET + FLASK APP
    socketio.run(app, host="100.75.51.60", port=4010, allow_unsafe_werkzeug=True)
