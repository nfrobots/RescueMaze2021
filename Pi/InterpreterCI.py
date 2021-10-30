from dataclasses import dataclass
from math import sqrt
from typing import List

from Pi.CalibratorCI import Calibrator, CalibrationTarget
from Pi.ReceiverCI import ArduinoData, Receiver
from RMMLIB4.Mapping import MazeTile
from RMMLIB4 import Constants
from RMMLIB4.Constants import RelDirection, Direction
from RMMLIB4 import Mapping
from util.Singleton import Singleton


def multidim_distance(a: List[int], b: List[int]) -> float:
    if len(a) != len(b):
        print("[ERROR] cannot find distance between points of different shape")
        return -1.0
    return sqrt(sum((a[i] - b[i])**2 for i in range(len(a))))


@dataclass
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
        self.calibrator.load_calibration()
        # assert self.calibrator.calibration_data != None

    def ir_data_extractor(self, data, target, *devices):
        calibrated = self.calibrator.get_calibration(target)
        dist = multidim_distance([getattr(data, device) for device in devices],
                                 [getattr(calibrated, device) for device in devices])
        return dist
        
    def interprete_data(self, data: ArduinoData):
        whiteness = (multidim_distance(data.get_rgba(), self.calibrator.get_calibration(CalibrationTarget.COLOR_WHITE).get_rgba()))
        redness   = (multidim_distance(data.get_rgba(), self.calibrator.get_calibration(CalibrationTarget.COLOR_RED).get_rgba()))

        walls = {
            RelDirection.FORWARD:   self.ir_data_extractor(data, CalibrationTarget.WALL_FRONT, "ir_2", "ir_3"),
            RelDirection.RIGHT:     self.ir_data_extractor(data, CalibrationTarget.WALL_RIGHT, "ir_4", "ir_5", "ultrasonic_right"),
            RelDirection.BACKWARD:  self.ir_data_extractor(data, CalibrationTarget.WALL_BACK,  "ir_6", "ir_7"),
            RelDirection.LEFT:      self.ir_data_extractor(data, CalibrationTarget.WALL_LEFT,  "ir_0", "ir_1", "ultrasonic_left") 
        }

        no_walls = {
            RelDirection.FORWARD:   self.ir_data_extractor(data, CalibrationTarget.NO_WALL_FRONT, "ir_2", "ir_3"),
            RelDirection.RIGHT:     self.ir_data_extractor(data, CalibrationTarget.NO_WALL_RIGHT, "ir_4", "ir_5", "ultrasonic_right"),
            RelDirection.BACKWARD:  self.ir_data_extractor(data, CalibrationTarget.NO_WALL_BACK,  "ir_6", "ir_7"),
            RelDirection.LEFT:      self.ir_data_extractor(data, CalibrationTarget.NO_WALL_LEFT,  "ir_0", "ir_1", "ultrasonic_left") 
        }

        ret = InterpretedData()

        for relDirection in RelDirection:
            ret._data[relDirection] = walls[relDirection] < no_walls[relDirection]

        ret._data[Constants.VICTIM] = redness < whiteness

        print(ret._data)
        
        return (whiteness, redness)
    
        

if __name__ == "__main__":
    i = Interpreter()
    print(i.calibrator.calibration_data)
    print(i.calibrator.calibration_data[CalibrationTarget.WALL_LEFT.value])
