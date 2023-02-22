import socket
import cv2

HOST_ADDRESS = 'localhost'
PORT = 1337

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

soc.connect((HOST_ADDRESS, PORT))

image = cv2.imread('Download.jpg')
_, image_enc = cv2.imencode('.jpg', image)
image_bytes = image_enc.tobytes()
length = len(image_bytes)

print(f"Captured Image of size {length}. Transmitting size info...")

soc.send(str(length).encode('utf8'))

ans = soc.recv(1024)
if ans.decode('utf8') == "OK":
    print("Host answered OK, sending all bytes")
else:
    print("ERROR. Host didn't accept the data")
    exit()

soc.sendall(image_bytes)


import numpy as np
array = np.frombuffer(image_bytes)
img = cv2.imdecode(array, cv2.IMREAD_COLOR)

cv2.imwrite('out.jpg', img)