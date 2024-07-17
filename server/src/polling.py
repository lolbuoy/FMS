from app import socketio, app, send_event
import logging
from redis_manager import get_redis_data

def poll_redis(name, interval):
    # LOGGING
    logger = logging.getLogger(name)
    # logger.info("REDIS POLL STARTING: POLLING EVERY %s SECONDS" % (interval,))

    # POLLING
    while True:

        # GET REDIS DATA
        full_flight_data = get_redis_data()
        flight_count = len(full_flight_data.keys())

        # LOG
        # logger.info("Polled redis, %s flights found" % (flight_count,))

        # W.S
        # send_event(full_flight_data)

        # POLL
        socketio.sleep(interval)
