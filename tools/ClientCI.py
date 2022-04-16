from RMMLIB4.Constants import RelDirection, VICTIM
from Pi.InterpreterCI import InterpretedData
import json
import socket

from Pi.CalibratorCI import CalibrationTarget
from util.Singleton import Singleton
from RMMLIB4 import Mapping
from RMMLIB4 import Constants

HOST_ADDR = '10.42.0.114'
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
            return func(*args, **kwargs)
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
        except TimeoutError:
            print("[ERROR] could not connect to horst")

    @_requires_connection(default_return={"error": 1})
    def request_data(self):
        self.socket.send("data\n".encode("utf-8"))
        json_bytes = self.socket.recv(1024)
        try:
            return json.loads(json_bytes.decode("utf-8"))
        except:
            print("[ERROR] could not decode or unserialize data")

    @_requires_connection()
    def request_interpreted(self):
        self.socket.send("i".encode("utf-8"))
        raw_data = self.socket.recv(1024).decode("utf-8")
        data_dict = json.loads(raw_data)

        i_data = InterpretedData()

        for key in data_dict:
            if key == str(RelDirection.FORWARD.value):
                i_data._data[RelDirection.FORWARD] = data_dict[key]
            elif key == str(RelDirection.RIGHT.value):
                i_data._data[RelDirection.RIGHT] = data_dict[key]
            elif key == str(RelDirection.BACKWARD.value):
                i_data._data[RelDirection.BACKWARD] = data_dict[key]
            elif key == str(RelDirection.LEFT.value):
                i_data._data[RelDirection.LEFT] = data_dict[key]
            elif key == "VICTIM":
                i_data._data[Constants.VICTIM] = data_dict[key]
            elif key == "RAMP":
                i_data._data[Constants.RAMP] = data_dict[key]
            elif key == "BLACK":
                i_data._data[Constants.BLACK] = data_dict[key]
                
        print(i_data._data)

        return i_data

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

    @_requires_connection()
    def request_map(self):
        self.socket.send("map".encode("utf-8"))
        resp = self.socket.recv(1024)
        return Mapping.Map._restore(json.loads(resp.decode("utf-8")))

if __name__ == "__main__":
    c: Client = Client()
    c.connect()
    print(c.request_data()) # (norddetuscher akzent) Oourranje ohne Fluchtfleisch
