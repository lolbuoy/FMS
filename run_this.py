import os
import subprocess
from git import Repo, InvalidGitRepositoryError, GitCommandError
import paho.mqtt.client as mqtt
import json
import time
from dronekit import connect, APIException

# Configuration
REPO_URL = "https://github.com/lolbuoy/test_automation.git"  # Replace with your actual repository URL
REPO_PATH = "test_stuff"  # Replace with your actual repository path
MQTT_BROKER = "100.75.51.60"  # Replace with your MQTT broker
MQTT_PORT = 1883
global sysid 
sysid = 0
VEHICLE_CONNECTION_STRING = 'tcp:127.0.0.1:5762'  # Replace with your vehicle's connection string
SCRIPT_PATH = os.path.join(REPO_PATH, "run.sh")  # Path to the run.sh script inside the repository

def clone_or_update_repo(repo_url, repo_path):
    if not os.path.exists(repo_path):
        print(f"Repository not found at {repo_path}, cloning...")
        try:
            Repo.clone_from(repo_url, repo_path)
            print(f"Repository cloned successfully from {repo_url} to {repo_path}")
        except GitCommandError as e:
            print(f"Failed to clone the repository: {e}")
            return False
    else:
        print(f"Repository already exists at {repo_path}")
        # Open the existing repo
        try:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            # Fetch latest changes
            origin.fetch()
            # Access the remote branch using `origin/HEAD`
            remote_commit = repo.refs['origin/HEAD'].commit.hexsha
            local_commit = repo.head.object.hexsha
            if local_commit != remote_commit:
                print("Local commit hash does not match the remote. Pulling the latest changes...")
                origin.pull()
                print("Repository updated successfully.")
            else:
                print("Local repository is up to date.")
        except InvalidGitRepositoryError:
            print(f"The path {repo_path} is not a valid Git repository")
            return False
        except GitCommandError as e:
            print(f"Failed to update the repository: {e}")
            return False
    return True

def get_repo_version(repo_path):
    try:
        repo = Repo(repo_path)
        commit_hash = repo.head.object.hexsha
        tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime, reverse=True)
        latest_tag = tags[0].name if tags else "No tags found"
        return commit_hash, latest_tag
    except InvalidGitRepositoryError:
        print(f"The path {repo_path} is not a valid Git repository")
        return None, None
    except Exception as e:
        print(f"An error occurred while getting repo version: {e}")
        return None, None

def connect_vehicle(connection_string):
    print(f"Connecting to vehicle on: {connection_string}")
    try:
        vehicle = connect(connection_string, wait_ready=True)
        print("Vehicle connected successfully!")
        return vehicle
    except APIException as e:
        print(f"Failed to connect to the vehicle: {e}")
        return None

def get_sysid_thismav(vehicle):
    print("Attempting to acquire SYSID_THISMAV parameter...")
    global MQTT_TOPIC
    global sysid
    for _ in range(5):  # Try up to 5 times
        try:
            sysid = vehicle.parameters['SYSID_THISMAV']
            print(f"SYSID_THISMAV = {sysid}")
            MQTT_TOPIC = f"setup/{int(sysid)}/version"
            return sysid
        except KeyError:
            print("Parameter SYSID_THISMAV not found. Retrying...")
            time.sleep(1)
        except Exception as e:
            print(f"An error occurred while getting SYSID_THISMAV: {e}")
            return None
    
    print("Failed to retrieve SYSID_THISMAV after multiple attempts")
    return None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Failed to connect to MQTT broker with result code {rc}")

def publish_version_and_sysid(client, commit_hash, latest_tag, sysid):
    data = {
        "version": commit_hash,
        "latest_tag": latest_tag,
        "timestamp": int(time.time() * 1000)
    }
    json_data = json.dumps(data)
    client.publish(MQTT_TOPIC, json_data)
    print(f"Published version and SYSID data to {MQTT_TOPIC}: {json_data}")


def run_shell_script(script_path):
    print(f"Executing Python script: {script_path}")
    try:
        # Use the appropriate command to run the Python script
        result = subprocess.run(["bash", script_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"Python script executed successfully. Output:\n{result.stdout.decode('utf-8')}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute Python script. Error:\n{e.stderr.decode('utf-8')}")
    except FileNotFoundError:
        print("Python not found. Ensure that Python is installed and accessible in your PATH.")


def main():
    # Clone the repository if it doesn't exist, or update it if it does
    if not clone_or_update_repo(REPO_URL, REPO_PATH):
        print("Exiting due to failure to clone or update the repository.")

    # Get repository version
    commit_hash, latest_tag = get_repo_version(REPO_PATH)
    
    if commit_hash is None:
        print("Failed to get repository version.")


    # Connect to the vehicle
    vehicle = connect_vehicle(VEHICLE_CONNECTION_STRING)
    if vehicle is None:
        print("Failed to connect to the vehicle. Exiting.")


    # Get SYSID_THISMAV
    sysid = get_sysid_thismav(vehicle)
    if sysid is None:
        print("Failed to get SYSID_THISMAV. Continuing with None value.")

    # Set up MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect

    # Connect to MQTT broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return

    # Publish version and SYSID data
    publish_version_and_sysid(client, commit_hash, latest_tag, sysid)

    # Disconnect from MQTT broker
    client.disconnect()
    print("Disconnected from MQTT broker")

    # Run the shell script
    if os.path.exists(SCRIPT_PATH):
        run_shell_script(SCRIPT_PATH)
    else:
        print(f"Shell script {SCRIPT_PATH} not found.")

    # Close vehicle connection
    vehicle.close()
    print("Vehicle connection closed")

if __name__ == "__main__":
    main()
