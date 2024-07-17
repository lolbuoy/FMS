from app import app
import datetime
import redis

# REDIS SETUP
redis_client = redis.from_url(app.config["REDIS_URL"], decode_responses=True)


def get_redis_data():
    # flights = redis_client.keys()
    # full_flight_data = {}
    # for flight_id in flights:
    #     print(flight_id)
    #     full_flight_data[flight_id] = redis_client.hgetall(flight_id)

    full_flight_data = {
        "drones_state": redis_client.hgetall("drones_state"),
        "last_received": redis_client.hgetall("last_received"),
    }

    return full_flight_data


def save_active_status(drone_id, change_to):
    if change_to == "active":
        redis_client.hset("drones_state", drone_id, "active")
    elif change_to == "landed":
        redis_client.hset("drones_state", drone_id, "landed")
    elif change_to == "remove":
        redis_client.hdel("drones_state", drone_id)
    else:
        print("INVALID STATUS!")


def save_last_received_message(drone_id):
    now = round(datetime.datetime.now().timestamp() * 1000)
    redis_client.hset("last_received", drone_id, now)


def get_active_status():
    return redis_client.hgetall("drones_state")


def get_last_received_messages():
    return redis_client.hgetall("last_received")
