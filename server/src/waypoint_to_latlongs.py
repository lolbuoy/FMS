def waypoint_to_latlongs(wps_text):
    waypoints = []
    for i in wps_text.split("\n"):
        params = i.split("\t")
        if len(params) > 5:
            lat = float(params[8])
            lon = float(params[9])
            # alt = params[10]
            if float(lat) != 0.0 and float(lon) != 0.0:
                waypoints.append([lat, lon])
    return waypoints


print(waypoint_to_latlongs(open("/Users/ranjithrd/Desktop/FMS/simul.waypoints").read()))
