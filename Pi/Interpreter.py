from RMMLIB4 import Constants, Mapping

import json
from math import sqrt, tanh

def distance_nn(a, b):
    distance = abs(a - b)
    return distance if distance != 0 else 1

def euk_distance_nd(a, b):
    return sqrt(sum((a[i] - b[i])**2 for i in range(len(a))))

INTERPREDED_DATA_TEMPLATE = Mapping.MAZE_TILE_TEMPLATE

# MAZE_TILE_TEMPLATE =  {
#     Constants.KNOWN: False,             # tile is known
#     Constants.Direction.NORTH: False,   # north wall existing
#     Constants.Direction.SOUTH: False,   # south wall existing
#     Constants.Direction.WEST: False,    # west wall existing
#     Constants.Direction.EAST: False,    # east wall existing
#     Constants.RAMP: False,              # ramp existing
#     Constants.VICTIM: False,            # victim existing
#     Constants.BLACK: False              # black tile existing
# }

K_TANH = 1.2

def interprete_data(raw_data):
    with open("Pi/data/data.json") as f:
        calibrated_data=json.load(f)

    victim_color    = calibrated_data["VICTIM_COLOR"]
    white_color     = calibrated_data["WHITE_COLOR"]
    black_greyscale = calibrated_data["BLACK_GREYSCALE"]
    white_greyscale = calibrated_data["WHITE_GREYSCALE"]

    data = INTERPREDED_DATA_TEMPLATE.copy()

    ######### DIVISION BY ZERO !!!!
    data["victim"] = 1-tanh((distance_nn(victim_color["red"], raw_data["RED"]) / distance_nn(victim_color["red"], white_color["red"])\
                         + distance_nn(victim_color["green"], raw_data["GRE"]) / distance_nn(victim_color["green"], white_color["green"])\
                         + distance_nn(victim_color["blue"],  raw_data["BLU"]) / distance_nn(victim_color["blue"],  white_color["blue"])\
                         + distance_nn(victim_color["alpha"], raw_data["ALP"]) / distance_nn(victim_color["alpha"], white_color["alpha"]) ) / 4 * K_TANH)

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