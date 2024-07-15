import requests
import time
from pymavlink import mavutil
import redis

# Specify the IP address and port of your Redis server
redis_ip = '100.75.51.60'  # Replace with your Redis server IP address
redis_port = 6379          # Default Redis port is 6379

# Create a Redis client
client = redis.StrictRedis(host=redis_ip, port=redis_port, decode_responses=True)

def send_hashed_data_to_redis(hash_name, data):
    try:
        client.hset(hash_name, mapping=data)
        print(f'Successfully set hash {hash_name} with data {data}')
    except redis.RedisError as e:
        print(f'Redis error: {e}')

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
        response.raise_for_status()  # Raise an exception for bad responses
        weather_data = response.json()
        
        # Extract relevant information
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
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown")

def connect_drone(connection_string):
    try:
        # Connect to the drone
        vehicle = mavutil.mavlink_connection(connection_string)
        
        # Wait for the first heartbeat
        vehicle.wait_heartbeat()
        print("Connected to drone!")
        return vehicle
    except Exception as e:
        print(f"Error connecting to drone: {e}")
        return None

def get_drone_data(vehicle):
    try:
        # Request GPS data
        vehicle.mav.request_data_stream_send(
            vehicle.target_system, vehicle.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_POSITION, 1, 1
        )
        
        # Wait for GPS data
        msg = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        
        lat = msg.lat / 1e7  # Latitude in degrees
        lon = msg.lon / 1e7  # Longitude in degrees
        alt = msg.relative_alt / 1000  # Altitude in meters
        
        return lat, lon, alt
    except Exception as e:
        print(f"Error getting drone data: {e}")
        return None, None, None

def get_cardinal_direction(degrees):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / (360. / len(directions))) % len(directions)
    return directions[index]

def arm_drone(vehicle):
    try:
        # Send the command to arm the drone
        vehicle.mav.command_long_send(
            vehicle.target_system, vehicle.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # Confirmation
            1,  # Arm
            0, 0, 0, 0, 0, 0  # Unused parameters
        )
        print("Arming the drone...")
    except Exception as e:
        print(f"Error arming drone: {e}")

def disarm_drone(vehicle):
    try:
        # Send the command to disarm the drone
        vehicle.mav.command_long_send(
            vehicle.target_system, vehicle.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # Confirmation
            0,  # Disarm
            0, 0, 0, 0, 0, 0  # Unused parameters
        )
        print("Disarming the drone...")
    except Exception as e:
        print(f"Error disarming drone: {e}")

if __name__ == "__main__":
    # Connect to the drone
    connection_string = 'tcp:127.0.0.1:5763'
    drone = connect_drone(connection_string)
    
    if drone:
        # Example of arming and disarming
        arm_drone(drone)
        time.sleep(10)  # Wait 10 seconds while armed
        disarm_drone(drone)
        
        while True:
            # Get drone's current position
            latitude, longitude, altitude = get_drone_data(drone)
            
            if latitude is not None and longitude is not None:
                print(f"Drone Position - Lat: {latitude}, Lon: {longitude}, Alt: {altitude}m")
                
                # Get weather data for drone's current position
                weather = get_weather(latitude, longitude)
                
                if weather:
                    print(f"Temperature: {weather['temperature']}°C")
                    print(f"Wind Speed: {weather['wind_speed']} m/s")
                    wind_cardinal = get_cardinal_direction(weather['wind_direction'])
                    print(f"Wind Direction: {weather['wind_direction']}° ({wind_cardinal})")
                    print(f"Weather: {interpret_weather_code(weather['weather_code'])}")
                    
                    # Prepare data to send to Redis
                    data = {
                        "FLT_ID": "TMDKTG001",
                        "lat": latitude,
                        "lon": longitude,
                        "alt": altitude,
                        "temperature": weather['temperature'],
                        "wind_speed": weather['wind_speed'],
                        "wind_direction": wind_cardinal,
                        "weather": interpret_weather_code(weather['weather_code'])
                    }
                    
                    # Send the data to Redis
                    send_hashed_data_to_redis("Bullet_ECHO", data)
                else:
                    print("Failed to retrieve weather data.")
            else:
                print("Failed to get drone position.")
            
            # Wait for a few seconds before the next update
            time.sleep(0.25)
    else:
        print("Failed to connect to the drone.")
