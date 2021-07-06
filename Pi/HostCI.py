# nfrobots host-client socket communication protocol (NFHCSCP):
#
# command arg arg2 ...\n
# 
# message begins with command
# args follow seperatd by spaces
# message ends with new line character (\n)
# 
# example:
# led 255 0 255\n 

import json
import socket
from dataclasses import asdict
from time import sleep

from Pi.InterpreterCI import Interpreter
from Pi.ReceiverCI import Receiver
from Pi.CalibratorCI import Calibrator, CalibrationTarget
from Pi.Devices import LEDs

HOST_ADDR = '10.42.0.21'
PORT = 1337


class Host:
    def __init__(self, timeout=12):
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(timeout)
        self.socket.bind((HOST_ADDR, PORT))

        self.COMMANDS = {
            "data":         self._send_data,
            "d":            self._send_data,
            "interpreted":  self._send_interpreted,
            "i":            self._send_interpreted,
            "calibrate":    self._handle_calibration,
            "c":            self._handle_calibration,
            "led":          self._set_leds,
            "l":            self._set_leds,
            "quit":         self._handle_quit,
            "q":            self._handle_quit,
            "rgb":          self._led_effect
        }

    def connect(self):
        self.socket.listen()
        print(f"[INFO] listening to port {PORT} on {HOST_ADDR}")
        try:
            self.connection, addr = self.socket.accept()
            self.connected = True
            print(f"[OK] connection accepted with adress {addr}")
        except socket.timeout:
            print("[ERROR] connection timeout")
            exit()

    def update(self):
        if not self.connected:
            print("[ERROR] can not update, if socket is not connected!")
            sleep(1)
            return
        msg = self.connection.recv(1024)
        if msg:
            msg = msg.decode('utf-8')
            lines = [line for line in msg.split('\n') if line]
            for line in lines:
                command, *args = line.split(' ')
                self.COMMANDS.get(command, lambda *args: print(f"[ERROR] command {command} not found!"))(*args)
                print(f"[INFO] executed command: {command} with args: {args}")

    def _send_data(self):
        data = Receiver(port="/dev/ttyACM0").get_data_s()
        json_bytes = json.dumps(asdict(data)).encode('utf-8')
        self.connection.sendall(json_bytes)

    def _send_interpreted(self):
        data = Receiver().get_data_s()
        i_data = Interpreter().interprete_data(data)
        self.connection.sendall(f"{i_data[0]} {i_data[1]}".encode("utf-8"))
    
    def _handle_calibration(self, calibration_target):
        calibrator: Calibrator = Calibrator()
        calibrator.load_calibration()
        calibrator.calibrate(CalibrationTarget(calibration_target))
        calibrator.save_calibration()

    def _handle_quit(self):
        print("[INFO] the program was closed by request aka ihm wurde siuzid begangen")
        exit()

    def _set_leds(self, r, g, b):
        print(r, g, b)
        LEDs().set_rgb(int(r), int(g), int(b))

    def _led_effect(self):
        LEDs().defqon_1()

if __name__ == "__main__":
    h = Host()
    h.connect()
    while True:
        h.update()
