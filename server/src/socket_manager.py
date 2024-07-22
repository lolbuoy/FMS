from app import socketio
from redis_manager import get_redis_data
from mqtt_manager import publish_command
from calculate_state_from_redis import calculate_state_from_redis


# # SOCKET
# @socketio.on("redis_update")
# def logRedisUpdate(h):
#     print("RECEIVED REDIS_UPDATE")
#     print(h)


@socketio.on("connect")
def on_connect():
    # auth_header = request.headers.get("Authorization")
    # print(auth_header)
    print("CLIENT CONNECTED")
    current_full_data = get_redis_data()
    socketio.emit("redis_update", current_full_data)


@socketio.on("get_active_flights")
def on_active_flights():
    socketio.emit("active_flights", get_redis_data())


@socketio.on("get_drone_status")
def on_get_drone_status():
    res = calculate_state_from_redis(get_redis_data())
    socketio.emit("drone_status", res)


@socketio.on("command_arm")
def on_arm(drone_id):
    publish_command(drone_id, "arm")


@socketio.on("command_disarm")
def on_disarm(drone_id):
    publish_command(drone_id, "disarm")
