import json
import time
from dataclasses import dataclass, field
from typing import Tuple

import serial
from util.Singleton import Singleton

from Pi.Devices import Sensors


@dataclass
class ArduinoData:
    valid: bool = False
    IR_0: int = 0
    IR_1: int = 0
    IR_2: int = 0
    IR_3: int = 0
    IR_4: int = 0
    IR_5: int = 0
    IR_6: int = 0
    IR_7: int = 0
    gyro: Tuple[int, int, int] = field(default_factory=lambda: list([0, 0, 0]))
    gyro_x: int = 0
    gyro_y: int = 0
    gyro_z: int = 0
    greyscale: int = 0
    temp_left: int = 0
    temp_right: int = 0
    
    def __getitem__(self, key):
        return getattr(self, key)

ARDUINO_DEVSTR_TO_PI_DEVSTR = {
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
    "GRS": "greyscale",
    "USL": "ultrasonic_left",
    "USR": "ultrasonic_right"
}


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
            print(f"[OK] serial connection established with info: '{setup_info}'")
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
            IR_0                = data_dict["IR0"],
            IR_1                = data_dict["IR1"],
            IR_2                = data_dict["IR2"],
            IR_3                = data_dict["IR3"],
            IR_4                = data_dict["IR4"],
            IR_5                = data_dict["IR5"],
            IR_6                = data_dict["IR6"],
            IR_7                = data_dict["IR7"],
            gyro              = [data_dict["GYX"], data_dict["GYY"], data_dict["GYZ"]],
            gyro_x              = data_dict["GYX"],
            gyro_y              = data_dict["GYY"],
            gyro_z              = data_dict["GYZ"],
            greyscale           = data_dict["GRS"],
            temp_left           = data_dict["TML"],
            temp_right          = data_dict["TMR"]
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
    rcv = Receiver()
    # rcv.connect()
    while(True):
        print(rcv.get_data_s())
        time.sleep(1)


    # there seems to be a pibcak