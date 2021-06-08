import json
import socket

from Pi.CalibratorCI import CalibrationTarget

HOST_ADDR = 'localhost'
PORT = 1337

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def __del__(self):
        self.request_quit()

    def connect(self):
        try:
            self.socket.connect((HOST_ADDR, PORT))
            self.connected = True
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
        # TODO: implement pls (❤´艸｀❤)
        if not self.connected:
            print("[WARNING] client tried to request something but was not connected")
            return
        pass

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


if __name__ == "__main__":
    c = Client()
    c.connect()
    c.request_calibration(CalibrationTarget.COLOR_SILVER)