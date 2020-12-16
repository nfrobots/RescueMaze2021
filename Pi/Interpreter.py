import json
import types
from math import sqrt, tanh

def distance(a, b):
    return abs(a - b)

def euk_distance_nd(a, b):
    return sqrt(sum((a[i] - b[i])**2 for i in range(len(a))))

INTERPREDED_DATA_TEMPLATE = {
    "wall_left": 0,
    "wall_front": 0,
    "wall_right": 0,
    "wall_back": 0,
    "wall_doubfrn": 0,
    "ramp": 0,
    "victim": 0,
    "black": 0
}

K_TANH = 1.2

with open("Pi/data/data.json") as f:
    sensor_data=json.load(f)

victim_color    = sensor_data["VICTIM_COLOR"]
white_color     = sensor_data["WHITE_COLOR"]
black_greyscale = sensor_data["BLACK_GREYSCALE"]
white_greyscale = sensor_data["WHITE_GREYSCALE"]


def interprete_data(raw_data):
    data = INTERPREDED_DATA_TEMPLATE.copy()

    ######### DIVISION BY ZERO !!!!
    data["victim"] = 1-tanh((distance(victim_color["red"],   raw_data["RED"]) / distance(victim_color["red"],   white_color["red"])\
                         + distance(victim_color["green"], raw_data["GRE"]) / distance(victim_color["green"], white_color["green"])\
                         + distance(victim_color["blue"],  raw_data["BLU"]) / distance(victim_color["blue"],  white_color["blue"])\
                         + distance(victim_color["alpha"], raw_data["ALP"]) / distance(victim_color["alpha"], white_color["alpha"]) ) / 4 * K_TANH)

#    data["victim"] = tanh(sqrt(((victim_color["red"]   - raw_data["RED"]) / distance(victim_color["red"],   white_color["red"]))**2\
#                             + ((victim_color["green"] - raw_data["GRE"]) / distance(victim_color["green"], white_color["green"]))**2\
#                             + ((victim_color["blue"]  - raw_data["BLU"]) / distance(victim_color["blue"],  white_color["blue"]))**2\
#                             + ((victim_color["alpha"] - raw_data["ALP"]) / distance(victim_color["alpha"], white_color["alpha"]))**2) / 4 * K_TANH)


    return data


if __name__ == "__main__":
    import json


    test_data = {
        "RED": 17,
        "GRE": 70,
        "BLU": 60,
        "ALP": 10,
        "GRS": 128
    }

    #print(json.dumps(interprete_data(test_data)))
    print(interprete_data(test_data))