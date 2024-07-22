import time
import json
import paho.mqtt.client as mqtt

# from flask_mqtt import Mqtt
from config import Config

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.connect(host=Config.MQTT_BROKER_URL, port=Config.MQTT_BROKER_PORT)

lat = 13.70
lon = 77.64
while True:
    client.publish(
        "drones/data/Bullet_TEST",
        json.dumps(
            {
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "alt": 850.045,
                "drone_id": "Bullet_TEST",
                "flt_id": "TMDKTG201",
                "temperature": 24.5,
                "weather": "Overcast",
                "windspeed": 3.23,
                "wind_direction": "WSW",
            }
        ),
    )
    lat += 0.01
    lon += 0.01
    time.sleep(1)
