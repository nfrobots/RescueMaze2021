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
            direction = Constants.Direction((robot.direction.value - relDirection.value) % 4)
            tile._data[direction] = self._data[relDirection]

        return tile
    

class Interpreter(Singleton):
    def _init(self):
        self.calibrator: Calibrator = Calibrator()
        # assert self.calibrator.calibration_data != None

    def evaluate_distance_to_calibrated(self, data: ArduinoData, target: CalibrationTarget, use_log: bool=False):
        distance_func = multidim_distance if not use_log else logarithmic_multidim_distance
        return sum(
            distance_func(
                [data[sensor] for sensor in calibration_target_to_sensors(target)],
                [calibration_v[sensor] for sensor in calibration_target_to_sensors(target)]
            )
            for calibration_v in self.calibrator.get_calibration_data(target)
        ) / len(self.calibrator.get_calibration_data(target))
        
    def interprete_data(self, data: ArduinoData):
        print(data)

        distance_func = lambda data, target: self.evaluate_distance_to_calibrated(data, target, use_log=False)

        wall_front = distance_func(data, CalibrationTarget.WALL_FRONT) < distance_func(data, CalibrationTarget.NO_WALL_FRONT)
        wall_left = distance_func(data, CalibrationTarget.WALL_LEFT) < distance_func(data, CalibrationTarget.NO_WALL_LEFT)
        wall_right = distance_func(data, CalibrationTarget.WALL_RIGHT) < distance_func(data, CalibrationTarget.NO_WALL_RIGHT)
        wall_back = distance_func(data, CalibrationTarget.WALL_BACK) < distance_func(data, CalibrationTarget.NO_WALL_BACK)
        
        interpreted_data = InterpretedData()
        interpreted_data._data[RelDirection.FORWARD] = wall_front
        interpreted_data._data[RelDirection.LEFT] = wall_left
        interpreted_data._data[RelDirection.RIGHT] = wall_right
        interpreted_data._data[RelDirection.BACKWARD] = wall_back

        interpreted_data._data[Constants.VICTIM] = distance_func(data, CalibrationTarget.HEAT_VICT_LEFT) < distance_func(data, CalibrationTarget.NO_HEAT_VICT_LEFT)

        return interpreted_data
    
        

if __name__ == "__main__":
    clb = Calibrator()


    i = Interpreter()

    print(i.interprete_data(ArduinoData(IR_2=65, IR_3=48))._data)
