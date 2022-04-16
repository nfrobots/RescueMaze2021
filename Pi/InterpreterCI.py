from dataclasses import dataclass
from math import sqrt, log
from typing import List

from RMMLIB4 import Constants, Mapping
from RMMLIB4.Constants import Direction, RelDirection
from RMMLIB4.Mapping import MazeTile
from util.Singleton import Singleton

from Pi.CalibratorCI import CalibrationTarget, Calibrator, calibration_target_to_sensors
from Pi.ReceiverCI import ArduinoData, Receiver


def multidim_distance(a: List[int], b: List[int]) -> float:
    if len(a) != len(b):
        print("[ERROR] cannot find distance between points of different shape")
        return -1.0
    return sqrt(sum((a[i] - b[i])**2 for i in range(len(a))))

def logarithmic_multidim_distance(a: List[int], b: List[int]) -> float:
    return log(multidim_distance(a, b))


class InterpretedData:
    _data = {
        RelDirection.FORWARD: False,
        RelDirection.RIGHT: False,
        RelDirection.BACKWARD: False,
        RelDirection.LEFT: False,
        
        Constants.VICTIM: False,
        Constants.RAMP: False,
        Constants.BLACK: False
    }

    def to_maze_tile(self, robot: Mapping._Vctr):
        tile = MazeTile()

        for key in (Constants.VICTIM, Constants.BLACK, Constants.RAMP):
            tile._data[key] = self._data[key]

        for relDirection in RelDirection:
            direction = Constants.Direction((robot.direction.value + relDirection.value) % 4)
            tile._data[direction] = self._data[relDirection]

        return tile
    

class Interpreter(Singleton):
    def _init(self):
        self.calibrator: Calibrator = Calibrator()
        # assert self.calibrator.calibration_data != None

    def evaluate_distance_to_calibrated(self, data: ArduinoData, target: CalibrationTarget, use_log: bool=False):
        """ Calculates average 'distance' to specified target using calibration data provided by 'Calibrator' Singleton. Can use logarithmic distance, if specified"""
        distance_func = multidim_distance if not use_log else logarithmic_multidim_distance
        return sum(
            distance_func(
                [data[sensor] for sensor in calibration_target_to_sensors(target)],
                [calibration_v[sensor] for sensor in calibration_target_to_sensors(target)]
            )
            for calibration_v in self.calibrator.get_calibration_data(target)
        ) / len(self.calibrator.get_calibration_data(target))

    def compare_targets(self, data: ArduinoData, target1: CalibrationTarget, target2: CalibrationTarget) -> bool:
        """Compares if ArduinoData fits target1 or target2. Returns True if ArduinoData fits target1"""
        distance_func = lambda data, target: self.evaluate_distance_to_calibrated(data, target, use_log=False)
        return distance_func(data, target1) < distance_func(data, target2)
        
    def interprete_data(self, data: ArduinoData) -> InterpretedData:

        interpreted_data = InterpretedData()
        interpreted_data._data[RelDirection.FORWARD]    = self.compare_targets(data, CalibrationTarget.WALL_FRONT, CalibrationTarget.NO_WALL_FRONT)
        interpreted_data._data[RelDirection.RIGHT]      = self.compare_targets(data, CalibrationTarget.WALL_RIGHT, CalibrationTarget.NO_WALL_RIGHT)
        interpreted_data._data[RelDirection.LEFT]       = self.compare_targets(data, CalibrationTarget.WALL_LEFT, CalibrationTarget.NO_WALL_LEFT)
        interpreted_data._data[RelDirection.BACKWARD]   = self.compare_targets(data, CalibrationTarget.WALL_BACK, CalibrationTarget.NO_WALL_BACK)

        interpreted_data._data[Constants.VICTIM]        = self.compare_targets(data, CalibrationTarget.HEAT_VICT_LEFT, CalibrationTarget.NO_HEAT_VICT_LEFT) \
                                                        or self.compare_targets(data, CalibrationTarget.HEAT_VICT_RIGHT, CalibrationTarget.NO_HEAT_VICT_RIGHT)

        return interpreted_data

if __name__ == "__main__":
    clb = Calibrator()


    i = Interpreter()

    print(i.interprete_data(ArduinoData(IR_2=20, IR_3=20)))
