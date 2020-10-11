import Receiver

import time
import socket

# HOST = '10.42.0.21'
HOST = '192.168.178.48'
PORT = 1337

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(5)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[INFO] listening to port {PORT} on {HOST}")
    try:
        conn, addr = s.accept()
    except socket.timeout:
        print("connection timeout")
        exit()
        
    with conn:
        while True:
            conn.sendall(Receiver.request_data_bytes())
            time.sleep(1)

print("closed")