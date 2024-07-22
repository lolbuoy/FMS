import time
from pymavlink import mavutil

# Establish the MAVLink connection
the_connection = mavutil.mavlink_connection('tcp:localhost:5763')

# Wait for the first heartbeat to set the system and component ID of the remote system
the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_component))

# Define possible states
STATE_IN_MISSION = "In-mission"
STATE_LANDED = "Landed"
STATE_ON_GROUND = "Online and flight is on ground"

# Initial state
curr_state = STATE_ON_GROUND
landed_time = None

def monitor_state(the_connection):
    global curr_state, landed_time  # Use global variables for current state and landed time

    # Check HEARTBEAT message
    msg = the_connection.recv_match(type='HEARTBEAT', blocking=False)
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
    msg_text = the_connection.recv_match(type='STATUSTEXT', blocking=False)
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

# Call the monitoring function
while True:
    monitor_state(the_connection)
    time.sleep(1)  # Add a short delay to avoid busy-waiting
