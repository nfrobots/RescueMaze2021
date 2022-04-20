from RMMLIB4 import Constants
from ReceiverCI import Receiver
from InterpreterCI import Interpreter

from time import sleep


def constrain(value, min_, max_):
    """just like the arduino constrain, except it's not a macro"""
    if value < min_:
        return min_
    elif value > max_:
        return max_
    else:
        return value

def generate_motor_instruction_string(m1: int, m2: int, m3: int, m4: int) -> bytes:
    """Generates bytes representing motor instructions.
    Motor values have to be in the range of a signed short: [-32768, 32767]"""

    out = b"m"
    m1 = constrain(m1, -32768, 32767)
    m2 = constrain(m2, -32768, 32767)
    m3 = constrain(m3, -32768, 32767)
    m4 = constrain(m4, -32768, 32767)
    return out + m1.to_bytes(2, 'big', signed=True) + m2.to_bytes(2, 'big', signed=True) \
               + m3.to_bytes(2, 'big', signed=True) + m4.to_bytes(2, 'big', signed=True)

turn_right_instruction  = generate_motor_instruction_string(520, -520, 520, -520)
turn_left_instruction   = generate_motor_instruction_string(-520, 520, -520, 520)
forward_instruction     = generate_motor_instruction_string(790, 790, 790, 790)
backward_instruction    = generate_motor_instruction_string(-790, -790, -790, -790)

def driveRobot(direction: Constants.relDirection):
    sensor_data = Receiver().get_data_s()

    if direction == Constants.RelDirection.RIGHT:
        Receiver().send(turn_right_instruction)
    elif direction == Constants.RelDirection.LEFT:
        Receiver().send(turn_left_instruction)
    elif direction == Constants.RelDirection.BACKWARD:
        Receiver().send(turn_left_instruction)
        Receiver().send(turn_left_instruction)

    sleep(2)

    encoder_data = [sensor_data.motor1_enc, sensor_data.motor2_enc, sensor_data.motor3_enc, sensor_data.motor4_enc]

    Receiver().send(forward_instruction)


    for _ in range(10):
        interpreted: Interpreter.InterpretedData = Interpreter().interprete_data(Receiver().get_data_s())
        if interpreted._data[Constants.BLACK]:
            sensor_data = Receiver().get_data_s()
            Receiver().send(generate_motor_instruction_string(encoder_data[0] - sensor_data.motor1_enc, encoder_data[1] - sensor_data.motor2_enc, encoder_data[2] - sensor_data.motor3_enc, encoder_data[3] - sensor_data.motor4_enc))
            return Constants.BLACK
        sleep(0.2)

    return True
        

def allign():
    pass


def deploy_rescue_kit():
    pass