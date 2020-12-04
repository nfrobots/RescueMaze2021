import Receiver

import time
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
                    data = Receiver.request_data_bytes()
                conn.sendall(data)
            elif incomeing_byte == b'q':
                break

print("[INFO] CONNECTION CLOSED")
print("[INFO] PROGRAMM FINISHED")