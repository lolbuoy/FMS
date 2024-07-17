from app import socketio
from redis_manager import get_redis_data
from mqtt_manager import publish_command

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

@socketio.on("get_active_flights")
def on_active_flights(_):
    socketio.emit("active_flights", get_redis_data())

@socketio.on("command_arm")
def on_arm(drone_id):
    publish_command(drone_id, "arm")

@socketio.on("command_disarm")
def on_disarm(drone_id):
    publish_command(drone_id, "disarm")
