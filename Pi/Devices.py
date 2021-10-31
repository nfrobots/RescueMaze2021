from enum import Enum


class Sensors(str, Enum):
    IR_0 = "IR_0"
    IR_1 = "IR_1"
    IR_2 = "IR_2"
    IR_3 = "IR_3"
    IR_4 = "IR_4"
    IR_5 = "IR_5"
    IR_6 = "IR_6"
    IR_7 = "IR_7"

    gyro = "gyro"
    greyscale = "greyscale"

    temp_left = "temp_left"
    temp_right = "temp_right"