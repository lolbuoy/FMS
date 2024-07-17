import threading
import json
import paho.mqtt.client as mqtt

# from flask_mqtt import Mqtt
from app import socketio, send_event
from config import Config
from redis_manager import save_active_status, save_last_received_message
from drone_commands import DRONE_COMMANDS

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.connect(host=Config.MQTT_BROKER_URL, port=Config.MQTT_BROKER_PORT)
client.publish("test", "test1")


def parse_mqtt_message_payload(message):
    return str(message.payload.decode("utf-8"))


def on_drone_data(drone_data_topic, drone_data):
    if "lat" in drone_data:
        drone_id = drone_data_topic.replace("drones/data/", "")

        print("Data for drone_id", drone_id)
        print(drone_data)

        drone_data_to_send = {"drone_id": drone_id}
        drone_data_to_send.update(drone_data)

        send_event(drone_data_to_send)

        save_last_received_message(drone_id)
    else:
        print("Invalid message (data/)")


def on_active_data(topic, new_drone_state):
    drone_id = topic.replace("drones/state/", "")

    VALID_DRONE_STATES = ["powered_off", "flying", "landed", "grounded", "disconnected"]

    if new_drone_state in VALID_DRONE_STATES:
        print("Drone active!")
        print(drone_id, new_drone_state)

        save_active_status(drone_id, new_drone_state)
    else:
        print("INVALID DRONE STATE ", new_drone_state)


def on_command_confirmation(topic, status):
    drone_id = topic.split("/")[1]

    confirmation_to_send = status
    confirmation_to_send["drone_id"] = drone_id

    print("CONFIRMATION RECEIVED:", drone_id)
    print(confirmation_to_send)
    send_event(confirmation_to_send, type="command_confirmation")


def on_message(client, data, message, properties=None):
    print(threading.get_ident())
    print("MESSAGE!")
    topic = message.topic
    if topic == "test":
        print(parse_mqtt_message_payload(message))
    elif topic.startswith("drones/data"):
        on_drone_data(topic, json.loads(parse_mqtt_message_payload(message)))
    elif topic.startswith("drones/state"):
        on_active_data(topic, json.loads(parse_mqtt_message_payload(message)))
    elif topic.startswith("commands/") and topic.endswith("/confirmation"):
        on_command_confirmation(topic, json.loads(parse_mqtt_message_payload(message)))
    else:
        print("Unknown topic!")
        print(topic)


def publish_command(drone_id, command):
    print("PUBLISHING COMMAND %s" % (command,))

    if command in DRONE_COMMANDS.keys():
        client.publish(
            "commands/" + drone_id + "/command", json.dumps(DRONE_COMMANDS.get(command))
        )
    else:
        print("COMMAND NOT VALID!")


def start_mqtt_manager():
    print("STARTING MQTT MANAGER!")
    print(threading.get_ident())

    client.subscribe("test")
    client.subscribe("drones/data/#")
    # client.subscribe("drones/data/Bullet_ECHO")
    client.subscribe("drones/state/#")
    client.subscribe("commands/+/confirmation")

    print("on message_called")

    client.on_message = on_message

    # client.loop_start()
    while True:
        client.loop()

        socketio.sleep()


# ONLY FOR TESTING!!!!
def start_mqtt_manager_forever():
    client.loop_forever()


# start_mqtt_manager_forever()
