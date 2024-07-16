from app import app
import redis

# REDIS SETUP
redis_client = redis.from_url(app.config["REDIS_URL"], decode_responses=True)

def get_redis_data():
    flights = redis_client.keys()
    full_flight_data = {}
    for flight_id in flights:
        full_flight_data[flight_id] = redis_client.get(flight_id)

    return full_flight_data