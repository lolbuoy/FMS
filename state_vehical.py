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

def monitor_state(the_connection):
    global curr_state  # Use global variable for current state

    # Check HEARTBEAT message
    msg = the_connection.recv_match(type='HEARTBEAT', blocking=True)
    if msg:
        # Check armed status
        armed = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED != 0
        # Check if the drone is in the air
        in_air = msg.system_status == mavutil.mavlink.MAV_STATE_ACTIVE

        if curr_state != STATE_IN_MISSION and armed and in_air:
            curr_state = STATE_IN_MISSION

        if curr_state == STATE_LANDED and not armed and not in_air:
            curr_state = STATE_ON_GROUND

    # Check STATUSTEXT message for landing status
    msg_text = the_connection.recv_match()
    if msg_text.get_type() == 'STATUSTEXT':
                print(msg_text.text)
                if "Land" in msg_text.text:
                    print("jaibalaya")
    if curr_state == STATE_IN_MISSION and msg_text and ("Land complete" or "PreArm: QLAND mode not armable") in msg_text.text:
        curr_state = STATE_LANDED

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
