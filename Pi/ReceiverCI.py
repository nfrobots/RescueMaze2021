import json
import time
import serial
from dataclasses import dataclass

from util.Singleton import Singleton

@dataclass
class ArduinoData:
    valid: bool
    long_distance_ir: int = 0
    ir_0: int = 0
    ir_1: int = 0
    ir_2: int = 0
    ir_3: int = 0
    ir_4: int = 0
    ir_5: int = 0
    ir_6: int = 0
    ir_7: int = 0
    gyro_x: int = 0
    gyro_y: int = 0
    gyro_z: int = 0
    color_red: int = 0
    color_green: int = 0
    color_blue: int = 0
    color_alpha: int = 0
    greyscale: int = 0
    ultrasonic_left: int = 0
    ultrasonic_right: int = 0
    
    def get_rgba(self):
        return [self.color_red, self.color_green, self.color_blue, self.color_alpha]

ARDUINO_DEVSTR_TO_PI_DEVSTR = {
    "LIR": "long_distance_ir",
    "IR0": "ir_0",
    "IR1": "ir_1",
    "IR2": "ir_2",
    "IR3": "ir_3",
    "IR4": "ir_4",
    "IR5": "ir_5",
    "IR6": "ir_6",
    "IR7": "ir_7",
    "GYX": "gyro_x",
    "GYZ": "gyro_y",
    "GYZ": "gyro_z",
    "RED": "color_red",
    "GRE": "color_green",
    "BLU": "color_blue",
    "ALP": "color_alpha",
    "GRS": "greyscale",
    "USL": "ultrasonic_left",
    "USR": "ultrasonic_right"
}

def arduino_devstr_to_py_devstr(arduino_devstr: str):
    return ARDUINO_DEVSTR_TO_PI_DEVSTR.get(arduino_devstr, None)

class Receiver(Singleton):
    def __init__(self, port=None):
        """Receiver is a singelton.

        Args:
            port (str, optional): serial device path/port. Defaults to '/dev/ttyACM0'.
        """
        if port and port != self.port:
            print(f"[WARNING] tried to create Receiver on port '{port}'. Port is already set to '{self.port}'")

    def _init(self, port='/dev/ttyACM0'):
        self.port = port
        self.REQUEST_BYTE = 'd'.encode('utf-8')
        self.connected = False

    def connect(self):
        self.serial_connection = serial.Serial(self.port, 9600, timeout=0.2)

        while self.serial_connection.in_waiting == 0:
            print("[INFO] waiting for Arduino to finish initialization and establish serial connection")
            time.sleep(0.5)
        
        try:
            setup_info = self.serial_connection.read(1024).decode('utf-8')
        except UnicodeDecodeError:
            print("[ERROR] could not decode setup info")
            setup_info = "[ERROR]"

        if "[ERROR]" in setup_info:
            print("[ERROR] connecting to Arduino failed")
        else:
            print(f"[OK] serial connection established with info: {setup_info}")
            self.connected = True

    def request_data_as_bytes(self):
        """Requests data from arduino and returns it as a bytes or None if error occured"""
        if not self.connected:
            print("[ERROR] Receiver is not connected!")
            return None

        self.serial_connection.write(self.REQUEST_BYTE)
        valid = True
        received_data = b''
        incomeing_char = self.serial_connection.read()
        
        while incomeing_char != b'}':
            if incomeing_char == b'':
                print("[WARNING] serial data request timed out")
                valid = False
                break

            received_data += incomeing_char
            incomeing_char = self.serial_connection.read()
        
        if valid:
            return received_data + b'}'
       #else:
       #    return None

    def get_data(self):
        """Requests data from arduino and returns it as a ArduinoData dataclass"""
        data_bytes = self.request_data_as_bytes()
        if data_bytes == None:
            return ArduinoData(valid=False)
        try:
            data_dict = json.loads(data_bytes)
        except json.decoder.JSONDecodeError:
            print("[ERROR] could not decode bytes to json")

        return ArduinoData(
            valid               = True,
            long_distance_ir    = data_dict["LIR"],
            ir_0                = data_dict["IR0"],
            ir_1                = data_dict["IR1"],
            ir_2                = data_dict["IR2"],
            ir_3                = data_dict["IR3"],
            ir_4                = data_dict["IR4"],
            ir_5                = data_dict["IR5"],
            ir_6                = data_dict["IR6"],
            ir_7                = data_dict["IR7"],
            gyro_x              = data_dict["GYX"],
            gyro_y              = data_dict["GYY"],
            gyro_z              = data_dict["GYZ"],
            color_red           = data_dict["RED"],
            color_green         = data_dict["GRE"],
            color_blue          = data_dict["BLU"],
            color_alpha         = data_dict["ALP"],
            greyscale           = data_dict["GRS"],
            ultrasonic_left     = data_dict["USL"],
            ultrasonic_right    = data_dict["USR"]
        )

    def get_data_s(self):
        """like get_data, but cannot return invalid"""
        if not self.connected:
            self.connect()

        data = self.get_data()
        while data.valid == False:
            data = self.get_data()
        return data


if __name__ == "__main__":
    rcv = Receiver(port='COM3')
    # rcv.connect()
    print(rcv.get_data_s())

    rcv2 = Receiver('asbs')
    print(rcv2.connected)