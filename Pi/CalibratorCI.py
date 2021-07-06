import json
from enum import Enum
from pathlib import Path

from Pi.ReceiverCI import Receiver, ArduinoData, arduino_devstr_to_py_devstr
from util.Singleton import Singleton

class CalibrationTarget(str, Enum):
    COLOR_RED         = "COLOR_RED"
    COLOR_WHITE       = "COLOR_WHITE"
    COLOR_SILVER      = "COLOR_SILVER"
    COLOR_BLACK       = "COLOR_BLACK"
    WALL_LEFT         = "WALL_LEFT"
    WALL_FRONT        = "WALL_FRONT"
    WALL_RIGHT        = "WALL_RIGHT"
    WALL_BACK         = "WALL_BACK"
    WALL_2ND_FRONT_LD = "WALL_2ND_FRONT_LD"
    NO_WALL_LEFT      = "NO_WALL_LEFT"
    NO_WALL_FRONT     = "NO_WALL_FRONT"
    NO_WALL_RIGHT     = "NO_WALL_RIGHT"
    NO_WALL_BACK      = "NO_WALL_BACK"
    NO_WALL_2ND_FRONT_LD = "NO_WALL_2ND_FRONT_LD"
    GYRO_FLAT         = "GYRO_FLAT"
    GYRO_INCLINE      = "GYRO_INCLINE"


class Calibrator(Singleton):

    def _init(self):
        self.path = Path(__file__).parent / 'data/data.json'
        self.calibration_data = {}

    def load_calibration(self):
        with open(self.path, 'r') as f:
            self.calibration_data = json.load(f)

    def save_calibration(self):
        if not self.calibration_data:
            print("[WARNING] trying to save empty calibration. Aborting...")
            return

        with open(self.path, 'w') as f:
            json.dump(self.calibration_data, f)
        
    def calibrate(self, target: CalibrationTarget):
        sensor_data = Receiver().get_data_s()
        # sensor_data = ArduinoData(valid=False)
        
        if target in (CalibrationTarget.COLOR_RED, CalibrationTarget.COLOR_WHITE,
                    CalibrationTarget.COLOR_SILVER, CalibrationTarget.COLOR_BLACK):
            self.calibration_data[target.value] = {
                "RED": sensor_data.color_red,
                "GRE": sensor_data.color_green,
                "BLU": sensor_data.color_blue,
                "ALP": sensor_data.color_alpha
            }
        elif target in (CalibrationTarget.WALL_LEFT, CalibrationTarget.NO_WALL_LEFT):
            self.calibration_data[target.value] = {
                "IR0": sensor_data.ir_0,
                "IR1": sensor_data.ir_1,
                "USL": sensor_data.ultrasonic_left
            }
        elif target in (CalibrationTarget.WALL_FRONT, CalibrationTarget.NO_WALL_FRONT):
            self.calibration_data[target.value] = {
                "IR2": sensor_data.ir_2,
                "IR3": sensor_data.ir_3,
                "LIR": sensor_data.long_distance_ir
            }
        elif target in (CalibrationTarget.WALL_RIGHT, CalibrationTarget.NO_WALL_RIGHT):
            self.calibration_data[target.value] = {
                "IR4": sensor_data.ir_4,
                "IR5": sensor_data.ir_5,
                "USR": sensor_data.ultrasonic_right
            }
        elif target in (CalibrationTarget.WALL_BACK, CalibrationTarget.NO_WALL_BACK):
            self.calibration_data[target.value] = {
                "IR6": sensor_data.ir_6,
                "IR7": sensor_data.ir_7
            }
        elif target in (CalibrationTarget.WALL_2ND_FRONT_LD, CalibrationTarget.NO_WALL_2ND_FRONT_LD):
            self.calibration_data[target.value] = {
                "LIR": sensor_data.long_distance_ir
            }
        elif target in (CalibrationTarget.GYRO_FLAT, CalibrationTarget.GYRO_INCLINE):
            self.calibration_data[target.value] = {
                "GYX": sensor_data.gyro_x,
                "GYY": sensor_data.gyro_y,
                "GYZ": sensor_data.gyro_z
            }
        else:
            print("[ERROR] calibration target is not implemented")

    def get_calibration(self, target: CalibrationTarget) -> ArduinoData:
        data = ArduinoData(valid=True)
        for key in self.calibration_data[target.value]:
            setattr(data, arduino_devstr_to_py_devstr(key), self.calibration_data[target][key])

        return data

if __name__ == '__main__':
    from pprint import pprint
    clb = Calibrator()
    clb2 = Calibrator()
    clb.load_calibration()

    pprint(clb.get_calibration(CalibrationTarget.COLOR_RED))

    # [clb.calibrate(a) for a in CalibrationTarget]
    # # pprint(clb.calibration_data)
    # # clb.save_calibration()

    # clb.calibrate(CalibrationTarget.COLOR_RED)
    # pprint(clb.calibration_data)
