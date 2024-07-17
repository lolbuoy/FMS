import paho.mqtt.client as mqtt
import json
from pymavlink import mavutil

# MQTT Configuration
MQTT_BROKER = "100.75.51.60"  # Replace with your MQTT broker address
MQTT_PORT = 1883  # Default MQTT port
DRONE_NAME_FILE = "drone_name.txt"  # File containing the drone's name

# MAVLink Configuration
MAVLINK_CONNECTION = 'tcp:localhost:5763'  # Replace with your MAVLink connection string

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

# Read the drone name and set the MQTT topics
DRONE_NAME = read_drone_name()
MQTT_COMMAND_TOPIC = f"commands/{DRONE_NAME}/command"
MQTT_CONFIRMATION_TOPIC = f"commands/{DRONE_NAME}/confirmation"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker. Subscribing to topic: {MQTT_COMMAND_TOPIC}")
        client.subscribe(MQTT_COMMAND_TOPIC)
    else:
        print(f"Failed to connect to MQTT broker with code {rc}")

def send_mavlink_command(mav_connection, command_data):
    try:
        mav_connection.mav.command_long_send(
            command_data.get("target_system", mav_connection.target_system),
            command_data.get("target_component", mav_connection.target_component),
            command_data["command"],  # command ID
            command_data.get("confirmation", 0),  # confirmation
            command_data.get("param1", 0),
            command_data.get("param2", 0),
            command_data.get("param3", 0),
            command_data.get("param4", 0),
            command_data.get("param5", 0),
            command_data.get("param6", 0),
            command_data.get("param7", 0)
        )

        # Wait for COMMAND_ACK message
        msg = mav_connection.recv_match(type='COMMAND_ACK', blocking=True)
        if msg:
            result = {
                "command": msg.command,
                "result": msg.result
            }
            return result
        else:
            print("No COMMAND_ACK received")
            return None
    except Exception as e:
        print(f"Error sending MAVLink command: {e}")
        return None

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"Received message on topic {msg.topic}:")
        print(f"Raw payload: {payload}")
        
        # Parse the JSON payload
        command_data = json.loads(payload)
        
        if isinstance(command_data, dict) and "command" in command_data:
            print(f"Received command data: {command_data}")
            
            # Process the command
            result = send_mavlink_command(mav_connection, command_data)
            if result:
                client.publish(MQTT_CONFIRMATION_TOPIC, json.dumps(result))
                print(f"Sent command {command_data['command']}, result: {result}")
            else:
                print(f"Failed to receive confirmation for command {command_data['command']}")
        else:
            print("Received data is not a valid command dictionary or missing 'command' key.")
            print(json.dumps(command_data, indent=2))
        
        print("---")  # Separator for multiple messages
    except json.JSONDecodeError:
        print("Error: Received payload is not valid JSON")
    except Exception as e:
        print(f"Error processing message: {e}")

if __name__ == "__main__":
    print(f"Using drone name: {DRONE_NAME}")
    
    # Set up MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Set up MAVLink connection
    mav_connection = mavutil.mavlink_connection(MAVLINK_CONNECTION)
    
    try:
        # Connect to MQTT broker
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Attempting to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        
        # Wait for the MAVLink connection to be established
        mav_connection.wait_heartbeat()
        print("MAVLink connection established")
        
        # Start the MQTT loop
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("Script is shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        mqtt_client.disconnect()
        print("Disconnected from MQTT broker")
        mav_connection.close()
        print("Closed MAVLink connection")
