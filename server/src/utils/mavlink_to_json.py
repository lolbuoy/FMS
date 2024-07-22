def mavlink_to_json(mavlink_data, drone_id):
    mavlink_data.update({"drone_id": drone_id})
    return mavlink_data
