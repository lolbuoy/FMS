import json
import time
from pymavlink import mavutil
import paho.mqtt.client as mqtt
import requests
from math import radians, sin, cos, sqrt, atan2

# MQTT Configuration
MQTT_BROKER = "100.75.51.60"  # Replace with your MQTT broker address
MQTT_PORT = 1883  # Default MQTT port
DRONE_NAME_FILE = "drone_name.txt"  # File containing the drone's name

# Drone Configuration
DRONE_CONNECTION = 'tcp:127.0.0.1:5763'

# States
STATE_IN_MISSION = "In_mission"
STATE_LANDED = "Landed"
STATE_ON_GROUND = "Online and flight is on ground"

# Initial state
curr_state = STATE_ON_GROUND
landed_time = None

# for distance calculation
last_lat = None
last_lon = None
total_distance = 0.0

critical_voltage = 14  # in volts

actual_voltage = critical_voltage * 1000  # Don't do anything with this

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

def monitor_state(vehicle):
    global curr_state, landed_time  # Use global variables for current state and landed time

    # Check HEARTBEAT message
    msg = vehicle.recv_match(type='HEARTBEAT', blocking=False)
    if msg:
        # Check armed status
        armed = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED != 0
        # Check if the drone is in the air
        in_air = msg.system_status == mavutil.mavlink.MAV_STATE_ACTIVE

        if curr_state != STATE_IN_MISSION and armed and in_air:
            curr_state = STATE_IN_MISSION

        if curr_state == STATE_LANDED and not armed and not in_air:
            if landed_time and (time.time() - landed_time >= 10):
                curr_state = STATE_ON_GROUND
                landed_time = None  # Reset landed time

    # Check STATUSTEXT message for landing status
    msg_text = vehicle.recv_match(type='STATUSTEXT', blocking=False)
    if msg_text:
        if hasattr(msg_text, 'text'):
            print(f"Received STATUSTEXT message: {msg_text.text}")

            # Check if the text contains "Land complete"
            if curr_state == STATE_IN_MISSION or "Land complete" in msg_text.text:
                curr_state = STATE_LANDED
                landed_time = time.time()  # Record the time when landed

    # Print current state
    if curr_state == STATE_IN_MISSION:
        print(">> In-mission")
    elif curr_state == STATE_LANDED:
        print(">> Landed")
    elif curr_state == STATE_ON_GROUND:
        print(">> Online and flight is on ground")

    # Return the current state
    return curr_state

def battry_voltage(vehicle):
        try:
            # Voltage monitoring
            vehicle.mav.request_data_stream_send(
                vehicle.target_system,
                vehicle.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_EXTENDED_STATUS,
                1,  # Hz
                1,  # start sending
            )
            voltage_msg = vehicle.recv_match(type='SYS_STATUS', blocking=False, timeout=1)
            if voltage_msg:
                voltage_battery = voltage_msg.voltage_battery
                print(f"Voltage: {voltage_battery / 1000} V")
                if voltage_battery < actual_voltage:
                    print("Warning: Voltage too low. Consider replacing or recharging the battery.")
                    change = (actual_voltage - voltage_battery) / 1000
                    print(f"Actual Voltage: {voltage_battery / 1000} V, Difference: {change} V")
            return voltage_battery , change
        except Exception as e:
            print(f"Monitoring Error: {e}")

def get_drone_data(vehicle):
    global last_lat, last_lon, total_distance, curr_state, landed_time
    try:
        vehicle.mav.request_data_stream_send(
            vehicle.target_system, vehicle.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_POSITION, 1, 1
        )
        msg = vehicle.recv_match(type='GLOBAL_POSITION_INT')
        if not msg:
            return None, None, None, None, None, None

        lat = msg.lat / 1e7
        lon = msg.lon / 1e7
        alt = msg.relative_alt / 1000
        
        vx = msg.vx / 100.0  # in m/s
        vy = msg.vy / 100.0  # in m/s
        vz = msg.vz / 100.0  # in m/s

        # Calculate total speed
        total_speed = (vx**2 + vy**2 + vz**2)**0.5
        total_speed = round(total_speed, 1)

        # Check HEARTBEAT message
        heartbeat_msg = vehicle.recv_match(type='HEARTBEAT', blocking=False)
        if heartbeat_msg:
            # Check armed status
            armed = heartbeat_msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED != 0
            # Check if the drone is in the air
            in_air = heartbeat_msg.system_status == mavutil.mavlink.MAV_STATE_ACTIVE

            # Print debug info
            print(f"Armed: {armed}, In air: {in_air}, Current state: {curr_state}")

            if curr_state != STATE_IN_MISSION or armed or in_air:
                curr_state = STATE_IN_MISSION
                print(f"State changed to: {curr_state}")

            if curr_state == STATE_LANDED and not armed and not in_air:
                if landed_time and (time.time() - landed_time >= 10):
                    curr_state = STATE_ON_GROUND
                    landed_time = None  # Reset landed time
                    print(f"State changed to: {curr_state}")

        # Check STATUSTEXT message for landing status
        statustext_msg = vehicle.recv_match(type='STATUSTEXT', blocking=False)
        if statustext_msg and hasattr(statustext_msg, 'text'):
            print(f"Received STATUSTEXT message: {statustext_msg.text}")

            # Check if the text contains "Land complete"
            if curr_state == STATE_IN_MISSION and "Land complete" in statustext_msg.text:
                curr_state = STATE_LANDED
                landed_time = time.time()  # Record the time when landed
                print(f"State changed to: {curr_state}")

        # Calculate distance between current and last position
        if last_lat is not None and last_lon is not None:
            R = 6371000.0  # Earth radius in meters

            lat1_rad = radians(last_lat)
            lon1_rad = radians(last_lon)
            lat2_rad = radians(lat)
            lon2_rad = radians(lon)

            dlon = lon2_rad - lon1_rad
            dlat = lat2_rad - lat1_rad

            a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            dist = R * c
            total_distance += dist
            total_distance = round(total_distance, 1)

        # Update last position
        last_lat = lat
        last_lon = lon
        
        return lat, lon, alt, total_speed, curr_state, total_distance
    except Exception as e:
        print(f"Error getting drone data: {e}")
        return None, None, None, None, None, None

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
            latitude, longitude, altitude, speed, state, total_distance = get_drone_data(drone)
            varification = monitor_state(drone)
            battry , diff = battry_voltage(drone)
            if latitude is not None and longitude is not None:
                print(f"Drone Position - Lat: {latitude}, Lon: {longitude}, Alt: {altitude}m, Speed: {speed:.1f}m/s, State: {state}, Total Distance: {total_distance:.1f}m")
                
                weather = get_weather(latitude, longitude)
                
                if weather:
                    wind_cardinal = get_cardinal_direction(weather['wind_direction'])
                    
                    data = {
                        "flt_id": "TMDKTG001",
                        "lat": latitude,
                        "lon": longitude,
                        "alt": altitude,
                        "speed": speed,
                        "battry_voltace": battry,
                        "below_critical": diff,
                        "state": state,
                        "state_verification": varification,
                        "total_distance": total_distance,
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
