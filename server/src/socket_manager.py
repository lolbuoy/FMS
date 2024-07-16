from app import socketio
from redis_manager import get_redis_data

# SOCKET
@socketio.on("redis_update")
def logRedisUpdate(h):
    print("RECEIVED REDIS_UPDATE")
    print(h)


@socketio.on("connect")
def on_connect():
    print("CLIENT CONNECTED")
    current_full_data = get_redis_data()
    socketio.emit("redis_update", current_full_data)


def send_event(data):
    print(data)
    socketio.emit("redis_update", data, include_self=True)