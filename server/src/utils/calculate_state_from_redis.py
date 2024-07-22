from datetime import datetime


def calculate_status(status, recently_active):
    if status == "flying" and recently_active:
        return "flying"
    elif status == "flying" and not recently_active:
        return "disconnected"
    elif status == "on_ground" and recently_active:
        return "on_ground"
    elif status == "on_ground" and not recently_active:
        return "powered_off"
    elif status == "landed":
        return "landed"
    else:
        return "powered_off"


def calculate_state_from_redis(redis_state):
    print(redis_state)

    final_drone_state = {}
    now = round(datetime.now().timestamp() * 1000)
    for drone_id in redis_state["last_received"]:
        drone_last_received = redis_state["last_received"].get(drone_id, 0)
        seconds_since_last_received = (now - drone_last_received) / 1000

        status = redis_state[drone_id]  # flying | on_ground | landed
        recently_active = seconds_since_last_received < (5 * 60)

        calculated_status = calculate_status(status, recently_active)

        final_drone_state[drone_id] = calculated_status

    return final_drone_state
