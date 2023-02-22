import socket

HOST_ADDRESS = 'localhost'
PORT = 1337

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
soc.bind((HOST_ADDRESS, PORT))

print(f"[DEBUG] binding socket to ({HOST_ADDRESS}, {PORT})")

soc.settimeout(10)

soc.listen()

try:
    connection, addr = soc.accept()
except socket.timeout:
    print("[ERROR] socket timed out")
    exit()

print(f"[DEBUG] connection established to {addr}")

length = connection.recv(1024)
length = int(length.decode('utf-8'))
print(f"[INFO] receiving image size: {length}")

connection.send("OK".encode('utf-8'))

data = connection.recv(length)

if len(data) == length:
    print(f"[OK] received image of size {len(data)}")
else:
    print("[ERROR], dindn't receive all bytes")
    exit()

import cv2
import numpy as np


array = np.frombuffer(data)
img = cv2.imdecode(array, cv2.IMREAD_COLOR)

cv2.imwrite('out.jpg', img)
