import json
import socket

from Pi.CalibratorCI import CalibrationTarget
from util.Singleton import Singleton

HOST_ADDR = '10.42.0.21'
PORT = 1337


# decorator for requiring connection inside Client class 
def _requires_connection(default_return=None):
    if hasattr(default_return, "__call__"):
        print("[WARNING] you may have forgotten the '()' at '_requires_connection'")
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not args[0].connected:
                print(f"[WARNING] client tried to run '{func.__name__}' but was not connected")
                return default_return
            func(*args, **kwargs)
        return wrapper
    return decorator


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

    @_requires_connection(default_return={"error": 1})
    def request_data(self):
        self.socket.send("d\n".encode("utf-8"))
        json_bytes = self.socket.recv(1024)
        try:
            return json.loads(json_bytes.decode("utf-8"))
        except:
            print("[ERROR] could not decode or unserialize data")

    @_requires_connection()
    def request_interpreted(self):
        self.socket.send("i".encode("utf-8"))
        raw_data = self.socket.recv(1024).decode("utf-8")
        data = raw_data.split(" ")
        return (float(data[0]), float(data[1]))

    @_requires_connection()
    def request_calibration(self, calibration_target: CalibrationTarget):
        self.socket.send(f"c {calibration_target}\n".encode("utf-8"))

    @_requires_connection()
    def request_quit(self):
        self.socket.send("q\n".encode("utf-8"))

    @_requires_connection()
    def request_led(self, r, g, b):
        self.socket.send(f"l {r} {g} {b}\n".encode("utf-8"))

    @_requires_connection()
    def request_rgb_effect(self):
        self.socket.send("rgb".encode("utf-8"))

if __name__ == "__main__":
    c: Client = Client()
    # c.connect()
    # c.request_calibration(CalibrationTarget.COLOR_SILVER)
    print(c.request_data()) # (norddetuscher akzent) Oourranje ohne Fluchtfleisch