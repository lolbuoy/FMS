import json
import requests
from app import app
from config import Config
from socket_manager import socketio
from utils.waypoint_to_latlongs import waypoint_to_latlongs


@app.route("/")
def index():
    print(app.config)
    return "Hello, Flask-SocketIO!"


@app.route("/update_webhook")
def updateWebhook():
    print("SUPABASE WEBHOOK CALLED")
    socketio.emit("supabase_changed")

    return "", 200


@app.route("/get_supabase_data")
def getSupabaseData():
    supabase_headers = {
        "apikey": Config.SUPABASE_SERVICE_KEY,
        "Authorization": "Bearer " + Config.SUPABASE_SERVICE_KEY,
    }

    supabase_data_response = requests.get(
        Config.SUPABASE_URL + "/rest/v1/drones?select=*",
        headers=supabase_headers,
    )
    supabase_data = supabase_data_response.json()

    for i in range(len(supabase_data)):
        if "flight_route" in supabase_data[i]:
            try:
                waypoint_file = requests.get(
                    Config.SUPABASE_URL
                    + "/storage/v1/object/authenticated/redwing/"
                    + supabase_data[i]["flight_route"],
                    headers=supabase_headers,
                )
                supabase_data[i]["flight_data"] = waypoint_to_latlongs(
                    waypoint_file.text
                )
            except:
                supabase_data[i]["flight_data"] = "ERROR PROCESSING WAYPOINTS FILE!"

    return json.dumps(supabase_data)
