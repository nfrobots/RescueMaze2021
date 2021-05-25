from Pi import Receiver

import json

def calibrate(value_string):
    with open("/home/pi/nfrobots/RescueMaze2021/Pi/data/data.json", "r") as f:
        data = json.load(f)
    sensor_data = Receiver.get_data_s()
    if value_string == "VICTIM_COLOR":
        data["VICTIM_COLOR"]["red"]   = sensor_data["RED"]
        data["VICTIM_COLOR"]["green"] = sensor_data["GRE"]
        data["VICTIM_COLOR"]["blue"]  = sensor_data["BLU"]
        data["VICTIM_COLOR"]["alpha"] = sensor_data["ALP"]

    if value_string == "WHITE_COLOR":
        data["WHITE_COLOR"]["red"]   = sensor_data["RED"]
        data["WHITE_COLOR"]["green"] = sensor_data["GRE"]
        data["WHITE_COLOR"]["blue"]  = sensor_data["BLU"]
        data["WHITE_COLOR"]["alpha"] = sensor_data["ALP"]

    with open("/home/pi/nfrobots/RescueMaze2021/Pi/data/data.json", "w") as f:
        json.dump(data, f)
