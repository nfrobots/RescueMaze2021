from numpy import diff
from RMMLIB4 import Constants
from ReceiverCI import Receiver
from InterpreterCI import Interpreter
from CalibratorCI import Calibrator, CalibrationTarget

from time import sleep

from tools.Simulation import interprete_data


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

turn_left_instruction  = generate_motor_instruction_string(520, -520, 520, -520)
turn_right_instruction   = generate_motor_instruction_string(-520, 520, -520, 520)
forward_instruction     = generate_motor_instruction_string(800, 800, 800, 800)
backward_instruction    = generate_motor_instruction_string(-790, -790, -790, -790)

def rotateRobot(relDirection: Constants.RelDirection):
    if relDirection == Constants.RelDirection.RIGHT:
        Receiver().send(turn_right_instruction)
        sleep(2)
    elif relDirection == Constants.RelDirection.LEFT:
        Receiver().send(turn_left_instruction)
        sleep(2)
    elif relDirection == Constants.RelDirection.BACKWARD:
        rotateRobot(Constants.RelDirection.LEFT)
        rotateRobot(Constants.RelDirection.LEFT)
        sleep(2)
    allign()

def driveRobot(direction: Constants.RelDirection):
    sensor_data = Receiver().get_data_s()
    if (sensor_data.IR_0 < 130) != (sensor_data.IR_7 < 130):
        print("SEMI WALL")
        Receiver().send(generate_motor_instruction_string(-200, -200, -200, -200))
        sleep(1)
        Receiver().send(generate_motor_instruction_string(100, -100, 100, -100))
        sleep(0.4)

    rotateRobot(direction)

    sensor_data = Receiver().get_data_s()
    encoder_data = [sensor_data.motor1_enc, sensor_data.motor2_enc, sensor_data.motor3_enc, sensor_data.motor4_enc]

    Receiver().send(forward_instruction)

    for _ in range(4):
        sensor_data = Receiver().get_data_s()
        interpreted: Interpreter.InterpretedData = Interpreter().interprete_data(sensor_data)
        #print(sensor_data)
        if interpreted._data[Constants.BLACK]:
            Receiver().send(generate_motor_instruction_string(encoder_data[0] - sensor_data.motor1_enc - 80, -encoder_data[1] + sensor_data.motor2_enc - 80, encoder_data[2] - sensor_data.motor3_enc - 80, -encoder_data[3] + sensor_data.motor4_enc - 80))
            print("BLACK TILE!!")
            sleep(1.5)
            return Constants.BLACK

    return True
        

def allign():
    moved = False
    sensor_data = Receiver().get_data_s()
    if not sensor_data.main_switch:
        return False
    for _ in range(2):
        if moved:
            sensor_data = Receiver().get_data_s()
            if not sensor_data.main_switch:
                return False

        interprete_data = Interpreter().interprete_data(sensor_data)

        #rotary allignment
        if interprete_data._data[Constants.RelDirection.LEFT]:
            difference = sensor_data.IR_6 - sensor_data.IR_2 # 6 - 2
            print("Left allign")
            print(difference)
        elif interprete_data._data[Constants.RelDirection.RIGHT]:
            difference = sensor_data.IR_1 - sensor_data.IR_3 ## 1 - 3
            print("Right allign")
            print(difference)

        if interprete_data._data[Constants.RelDirection.RIGHT] or interprete_data._data[Constants.RelDirection.LEFT]:
            difference = 2.2 * difference
            difference = int(difference)

            motor_instruction = generate_motor_instruction_string(difference, -difference, difference, -difference)
            Receiver().send(motor_instruction)
            if 600 > difference > 10:
                sleep(0.5)
                moved = True

        #distance allignment
        if moved:
            sensor_data = Receiver().get_data_s()
            if not sensor_data.main_switch:
                return False

        print(sensor_data)
        average_of_target = lambda target: sum(d[k] for d in Calibrator().calibration_data[target] for k in d) / (len(Calibrator().calibration_data[target] * len(Calibrator().calibration_data[target][0])))

        if interprete_data._data[Constants.RelDirection.FORWARD]:
            destination = average_of_target(CalibrationTarget.WALL_FRONT)
            difference = (sensor_data.IR_0 + sensor_data.IR_7) / 2 - destination
            print("Forward allign")
            print(destination, difference)
        elif interprete_data._data[Constants.RelDirection.BACKWARD]:
            destination = average_of_target(CalibrationTarget.WALL_BACK)
            difference = destination - (sensor_data.IR_4 + sensor_data.IR_5) / 2
            print("Backward allign")
            print(destination, difference)

        if interprete_data._data[Constants.RelDirection.FORWARD] or interprete_data._data[Constants.RelDirection.BACKWARD]:
            difference = 2.2 * difference
            difference = int(difference)

            motor_instruction = generate_motor_instruction_string(difference, difference, difference, difference)
            Receiver().send(motor_instruction)
            if difference > 10:
                sleep(0.5)
                moved = True

    sensor_data = Receiver().get_data_s()
    print(sensor_data)
    interpreted_data = Interpreter().interprete_data(sensor_data)
    if interpreted_data._data[Constants.RelDirection.LEFT]:
        if (sensor_data.IR_2 + sensor_data.IR_6) / 2 > 150:
            Receiver().send(generate_motor_instruction_string(-50, 50, -50, 50))
            print("progressive allign")
    if interpreted_data._data[Constants.RelDirection.RIGHT]:
        if (sensor_data.IR_1 + sensor_data.IR_3) / 2  > 150:
            Receiver().send(generate_motor_instruction_string(50, -50, 50, -50))
            print("progressive allign")

def deploy_rescue_kit():
    Receiver().send(b'k')
    sleep(1)

if __name__ == "__main__":
    #allign()
    allign()
    #deploy_rescue_kit()
    #destination = sum(d[k] for d in Calibrator().calibration_data[CalibrationTarget.WALL_FRONT] for k in d) / (len(Calibrator().calibration_data[CalibrationTarget.WALL_FRONT] * len(Calibrator().calibration_data[CalibrationTarget.WALL_FRONT][0])))

    #print(destination)
    #driveRobot(Constants.RelDirection.FORWARD)