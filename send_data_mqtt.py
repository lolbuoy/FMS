import json
import time
from pymavlink import mavutil
import paho.mqtt.client as mqtt
import requests

# MQTT Configuration
MQTT_BROKER = "100.75.51.60"  # Replace with your MQTT broker address
MQTT_PORT = 1883  # Default MQTT port
DRONE_NAME_FILE = "drone_name.txt"  # File containing the drone's name

# Drone Configuration
DRONE_CONNECTION = 'tcp:127.0.0.1:5763'

def read_drone_name():
    try:
        with open(DRONE_NAME_FILE, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: {DRONE_NAME_FILE} not found. Using default name.")
        return "DEFAULT_DRONE"
    except IOError as e:
        print(f"Error reading {DRONE_NAME_FILE}: {e}. Using default name.")
        return "DEFAULT_DRONE"

# Read the drone name and set the MQTT topic
DRONE_NAME = read_drone_name()
MQTT_TOPIC = f"drones/data/{DRONE_NAME}"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker. Publishing to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT broker with code {rc}")

def get_weather(latitude, longitude):
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "windspeed_unit": "ms"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        current_weather = weather_data["current_weather"]
        return {
            "temperature": current_weather["temperature"],
            "wind_speed": current_weather["windspeed"],
            "wind_direction": current_weather["winddirection"],
            "weather_code": current_weather["weathercode"]
        }
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def interpret_weather_code(code):
    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown")

def connect_drone(connection_string):
    try:
        vehicle = mavutil.mavlink_connection(connection_string)
        vehicle.wait_heartbeat()
        print("Connected to drone!")
        return vehicle
    except Exception as e:
        print(f"Error connecting to drone: {e}")
        return None

def get_drone_data(vehicle):
    try:
        vehicle.mav.request_data_stream_send(
            vehicle.target_system, vehicle.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_POSITION, 1, 1
        )
        msg = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.relative_alt / 1000
        return lat, lon, alt
    except Exception as e:
        print(f"Error getting drone data: {e}")
        return None, None, None

def get_cardinal_direction(degrees):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / (360. / len(directions))) % len(directions)
    return directions[index]

if __name__ == "__main__":
    print(f"Using drone name: {DRONE_NAME}")
    
    # Connect to MQTT broker
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    # Connect to the drone
    drone = connect_drone(DRONE_CONNECTION)
    
    if drone:
        while True:
            latitude, longitude, altitude = get_drone_data(drone)
            
            if latitude is not None and longitude is not None:
                print(f"Drone Position - Lat: {latitude}, Lon: {longitude}, Alt: {altitude}m")
                
                weather = get_weather(latitude, longitude)
                
                if weather:
                    wind_cardinal = get_cardinal_direction(weather['wind_direction'])
                    
                    data = {
                        "flt_id": "TMDKTG001",
                        "lat": latitude,
                        "lon": longitude,
                        "alt": altitude,
                        "temperature": weather['temperature'],
                        "wind_speed": weather['wind_speed'],
                        "wind_direction": wind_cardinal,
                        "weather": interpret_weather_code(weather['weather_code'])
                    }
                    
                    # Convert data to JSON and publish to MQTT
                    json_data = json.dumps(data)
                    client.publish(MQTT_TOPIC, json_data)
                    print(f"Published data: {json_data}")
                else:
                    print("Failed to retrieve weather data.")
            else:
                print("Failed to get drone position.")
            
            time.sleep(0.33333)
    else:
        print("Failed to connect to the drone.")

    client.loop_stop()
    client.disconnect()