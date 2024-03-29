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
    time: int = 0
    motor1_enc: int = 0
    motor2_enc: int = 0
    motor3_enc: int = 0
    motor4_enc: int = 0
    main_switch: bool = False

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
        self.serial_connection = serial.Serial(self.port, 9600, timeout=2)

        time.sleep(2)

        while not self.serial_connection.in_waiting > 22:
            print("[INFO] waiting for Arduino to finish initialization and establish serial connection")
            time.sleep(1)
        
        try:
            setup_info = self.serial_connection.read(1024).decode('utf-8')
        except UnicodeDecodeError:
            print("[ERROR] could not decode setup info")
            setup_info = "[ERROR]"

        if "[ERROR]" in setup_info:
            print(f"[ERROR] connecting to Arduino failed: {setup_info}")
        else:
            print(f"[OK] serial connection established with info: '{setup_info}'")
            self.connected = True

    def request_data_as_bytes(self):
        """Requests data from arduino and returns it as a bytes or None if error occured"""
        if not self.connected:
            print("[ERROR] Receiver is not connected!")
            time.sleep(1000)
            return None

        self.serial_connection.write(self.REQUEST_BYTE)
        valid = True
        received_data = b''
        time.sleep(0.1)
        incomeing_char = self.serial_connection.read()
        
        while incomeing_char != b'}':
            if incomeing_char == b'':
                print("[WARNING] serial data request timed out")
                print(f"just received: {received_data}")
                valid = False
                break

            received_data += incomeing_char
            incomeing_char = self.serial_connection.read()
        
        if valid:
            return received_data + b'}'
       #else:
       #    return None

    def get_data(self) -> ArduinoData:
        """Requests data from arduino and returns it as a ArduinoData dataclass"""
        data_bytes = self.request_data_as_bytes()
        if data_bytes == None:
            return ArduinoData(valid=False)
        try:
            data_dict = json.loads(data_bytes)
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
                gyro                = [data_dict["GYX"], data_dict["GYY"], data_dict["GYZ"]],
                gyro_x              = data_dict["GYX"],
                gyro_y              = data_dict["GYY"],
                gyro_z              = data_dict["GYZ"],
                greyscale           = data_dict["GRS"],
                temp_left           = data_dict["TMR"],
                temp_right          = data_dict["TML"],
                time                = data_dict["time"],
                motor1_enc          = data_dict["M1E"],
                motor2_enc          = data_dict["M2E"],
                motor3_enc          = data_dict["M3E"],
                motor4_enc          = data_dict["M4E"],
                main_switch         = data_dict["SWI"]
            )
        except json.decoder.JSONDecodeError:
            print("[ERROR] could not decode bytes to json")
            return ArduinoData(valid=False)


    def get_data_s(self) -> ArduinoData:
        """like get_data, but cannot return invalid"""
        while not self.connected:
            self.connect()
            time.sleep(1)

        data = self.get_data()
        while data.valid == False:
            print("[WARNING] invalid data. Trying again")
            self.serial_connection.close()
            self.connect()
            data = self.get_data()
        return data

    def send(self, message: bytes):
        if not self.connected:
            self.connect()

        self.serial_connection.write(message)


if __name__ == "__main__":
    rcv = Receiver()
    a = Receiver()
    # rcv.connect()
    while(True):
        print(rcv.get_data_s())
        time.sleep(1)


# ArduinoData(valid=True, IR_0=8190, IR_1=8191, IR_2=522, IR_3=8191, IR_4=92, IR_5=77, IR_6=602, IR_7=8191, gyro=[-0.0, 0.0, 0.04], gyro_x=-0.0, gyro_y=0.0, gyro_z=0.04, greyscale=165, temp_left=19.67, temp_right=18.85, time=874042)
# ArduinoData(valid=True, IR_0=8190, IR_1=8190, IR_2=521, IR_3=8190, IR_4=92, IR_5=80, IR_6=598, IR_7=8191, gyro=[0.0, 0.0, 0.0], gyro_x=0.0, gyro_y=0.0, gyro_z=0.0, greyscale=163, temp_left=20.11, temp_right=19.07, time=12608)
    # there seems to be a pibcak
