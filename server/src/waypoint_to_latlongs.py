def waypoint_to_latlongs(wps_text):
    waypoints = []
    for i in wps_text.split("\n"):
        params = i.split("\t")
        if len(params) > 5 and params[3] not in ["84", "85"]:
            lat = params[8]
            lon = params[9]
            # alt = params[10]
            waypoints.append([lat, lon])
    return waypoints


# print(waypoint_to_latlongs(open("/Users/ranjithrd/Desktop/FMS/simul.waypoints").read()))
