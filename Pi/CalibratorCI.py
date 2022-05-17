import json
from enum import Enum
from pathlib import Path

import typing

from Pi.ReceiverCI import Receiver, ArduinoData
from util.Singleton import Singleton
from Pi.Devices import Sensors

from typing import Dict, List

class CalibrationTarget(str, Enum):
    WALL_LEFT           = "WALL_LEFT"
    WALL_FRONT          = "WALL_FRONT"
    WALL_RIGHT          = "WALL_RIGHT"
    WALL_BACK           = "WALL_BACK"
    NO_WALL_LEFT        = "NO_WALL_LEFT"
    NO_WALL_FRONT       = "NO_WALL_FRONT"
    NO_WALL_RIGHT       = "NO_WALL_RIGHT"
    NO_WALL_BACK        = "NO_WALL_BACK"
    GYRO_FLAT           = "GYRO_FLAT"
    GYRO_INCLINE        = "GYRO_INCLINE"
    TILE_WHITE          = "TILE_WHITE"
    TILE_BLACK          = "TILE_BLACK"
    HEAT_VICT_LEFT      = "HEAT_VICT_LEFT"
    NO_HEAT_VICT_LEFT   = "NO_HEAT_VICT_LEFT"
    HEAT_VICT_RIGHT     = "HEAT_VICT_RIGHT"
    NO_HEAT_VICT_RIGHT  = "NO_HEAT_VICT_RIGHT"


CALIBRATION_TARGET_DEPENDENCIES: Dict[CalibrationTarget, List[Sensors]] = {
    CalibrationTarget.WALL_LEFT:    [Sensors.IR_2, Sensors.IR_6],
    CalibrationTarget.NO_WALL_LEFT: [Sensors.IR_2, Sensors.IR_6],

    CalibrationTarget.WALL_FRONT:       [Sensors.IR_0, Sensors.IR_7],
    CalibrationTarget.NO_WALL_FRONT:    [Sensors.IR_0, Sensors.IR_7],

    CalibrationTarget.WALL_RIGHT: [Sensors.IR_1, Sensors.IR_3],
    CalibrationTarget.NO_WALL_RIGHT: [Sensors.IR_1, Sensors.IR_3],

    CalibrationTarget.WALL_BACK: [Sensors.IR_4, Sensors.IR_5],
    CalibrationTarget.NO_WALL_BACK: [Sensors.IR_4, Sensors.IR_5],
    
    CalibrationTarget.GYRO_FLAT: [Sensors.gyro],
    CalibrationTarget.GYRO_INCLINE: [Sensors.gyro],
    
    CalibrationTarget.TILE_WHITE: [Sensors.greyscale],
    CalibrationTarget.TILE_BLACK: [Sensors.greyscale],

    CalibrationTarget.HEAT_VICT_LEFT: [Sensors.temp_left],
    CalibrationTarget.NO_HEAT_VICT_LEFT: [Sensors.temp_left],

    CalibrationTarget.HEAT_VICT_RIGHT: [Sensors.temp_right],
    CalibrationTarget.NO_HEAT_VICT_RIGHT: [Sensors.temp_right]
}

def calibration_target_to_sensors(target: CalibrationTarget) -> List[Sensors]:
    """Returns a list of sensors that the specified calibration relies on."""
    return CALIBRATION_TARGET_DEPENDENCIES[target]


class Calibrator(Singleton):

    def _init(self):
        self.path = Path(__file__).parent / 'data/data.json'
        self.calibration_data: typing.Dict[CalibrationTarget, typing.List[typing.Dict[Sensors, float]]]= {}
        self.load_calibration()

    def load_calibration(self):
        if self.calibration_data:
            return

        try:
            with open(self.path, 'r') as f:
                self.calibration_data = json.load(f)
            return True
        except IOError:
            self.calibration_data = {}
            print("[WARNING] Calibration data file could not be opened")
            return False

    def save_calibration(self):
        if not self.calibration_data:
            print("[WARNING] trying to save empty calibration. Aborting...")
            return

        with open(self.path, 'w') as f:
            json.dump(self.calibration_data, f)
        
    def calibrate(self, target: CalibrationTarget):
        sensor_data = Receiver().get_data_s()
        # sensor_data = ArduinoData(valid=False)
        
        if not target in self.calibration_data:
            self.calibration_data[target] = []

        calibration_sensor_values = {}

        for sensor in CALIBRATION_TARGET_DEPENDENCIES[target]:
            calibration_sensor_values[sensor] = sensor_data[sensor]

        self.calibration_data[target].append(calibration_sensor_values)

    def get_calibration_data(self, target: CalibrationTarget):
        return self.calibration_data[target]

if __name__ == '__main__':
    from pprint import pprint
    clb = Calibrator()

#    clb.calibrate(CalibrationTarget.WALL_FRONT)
#    clb.calibrate(CalibrationTarget.WALL_FRONT)
#    clb.calibrate(CalibrationTarget.WALL_RIGHT)
#    clb.calibrate(CalibrationTarget.NO_WALL_RIGHT)

#    print(clb.get_calibration_data(CalibrationTarget.WALL_FRONT))

    print(clb.calibration_data)

    # print(json.loads(json.dumps(clb.calibration_data)) == clb.calibration_data) # -> True!!!! : )