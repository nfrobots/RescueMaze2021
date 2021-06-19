import json
import socket

from Pi.CalibratorCI import CalibrationTarget
from util.Singleton import Singleton

HOST_ADDR = '10.42.0.21'
PORT = 1337

class Client(Singleton):
    def _init(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def __del__(self):
        self.request_quit()

    def connect(self):
        try:
            self.socket.connect((HOST_ADDR, PORT))
            self.connected = True
            print("[INFO] connected successfully")
        except:
            print("[ERROR] could not connect to horst")

    def request_data(self):
        if not self.connected:
            print("[WARNING] client tried to request something but was not connected")
            return
        self.socket.send("d\n".encode("utf-8"))
        json_bytes = self.socket.recv(1024)
        try:
            return json.loads(json_bytes.decode("utf-8"))
        except:
            print("[ERROR] could not decode or unserialize data")

    def request_interpreted(self):
        if not self.connected:
            print("[WARNING] client tried to request something but was not connected")
            return
        self.socket.send("i".encode("utf-8"))
        raw_data = self.socket.recv(1024).decode("utf-8")
        data = raw_data.split(" ")
        return (float(data[0]), float(data[1]))
    


    def request_calibration(self, calibration_target: CalibrationTarget):
        if not self.connected:
            print("[WARNING] client tried to request something but was not connected")
            return
        self.socket.send(f"c {calibration_target}\n".encode("utf-8"))

    def request_quit(self):
        if not self.connected:
            print("[WARNING] client tried to request something but was not connected")
            return
        self.socket.send("q\n".encode("utf-8"))

    def request_led(self, r, g, b):
        if not self.connected:
            print("[WARNING] client tried to request something but was not connected")
            return
        self.socket.send(f"l {r} {g} {b}\n".encode("utf-8"))

    def request_rgb_effect(self):
        if not self.connected:
            print("[WARNING] client tried to request something but was not connected")
            return
        self.socket.send("rgb".encode("utf-8"))

if __name__ == "__main__":
    c = Client()
    c.connect()
    # c.request_calibration(CalibrationTarget.COLOR_SILVER)
    print(c.request_led(255, 71, 0)) # (norddetuscher akzent) Oourranje ohne Fluchtfleisch