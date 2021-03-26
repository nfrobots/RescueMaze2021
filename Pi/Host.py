import Receiver
import Interpreter
import Calibrator
import Devices

import time
import json
import socket

HOST = '10.42.0.21'
#HOST = '192.168.178.48'
PORT = 1337

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(6)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[INFO] listening to port {PORT} on {HOST}")
    try:
        conn, addr = s.accept()
        print(f"[OK] connection accepted with adress {addr}")
    except socket.timeout:
        print("connection timeout")
        exit()
        
    with conn:

        while True:
            incomeing_byte = conn.recv(1)
            if incomeing_byte == b'd':
                data = None
                while data == None:
                    data = json.dumps(Interpreter.interprete_data(Receiver.get_data())).encode('utf-8')
                conn.sendall(data)
            elif incomeing_byte == b'c':
                value_string = conn.recv(1024).decode('utf-8')
                print(value_string)
                Calibrator.calibrate(value_string)
            elif incomeing_byte == b'l':
                rgb_string = conn.recv(1024).decode('utf-8')
                r, g, b = rgb_string.split(" ")
                Devices.leds.fill((int(r), int(g), int(b)))
            elif incomeing_byte == b'q':
                break

print("[INFO] CONNECTION CLOSED")
print("[INFO] PROGRAMM FINISHED")