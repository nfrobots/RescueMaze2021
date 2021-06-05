from math import sqrt, tanh
from typing import List

from Pi.CalibratorCI import Calibrator, CalibrationTarget
from Pi.ReceiverCI import ArduinoData, Receiver
from RMMLIB4.Mapping import MazeTile
from util.Singleton import Singleton


def multidim_distance(a: List[int], b: List[int]) -> float:
    if len(a) != len(b):
        print("[ERROR] cannot find distance between points of different shape")
        return -1.0
    return sqrt(sum((a[i] - b[i])**2 for i in range(len(a))))

class Interpreter(Singleton):
    def _init(self):
        self.calibrator: Calibrator = Calibrator()
        self.calibrator.load_calibration()
        # assert self.calibrator.calibration_data != None

    def interprete_data(self, data: ArduinoData) -> MazeTile:
        
        whiteness = tanh(multidim_distance(data.get_rgba(), self.calibrator.get_calibration(CalibrationTarget.COLOR_WHITE).get_rgba()))
        redness   = tanh(multidim_distance(data.get_rgba(), self.calibrator.get_calibration(CalibrationTarget.COLOR_RED).get_rgba()))
    
        

if __name__ == "__main__":
    i = Interpreter()
    print(i.calibrator.calibration_data)
