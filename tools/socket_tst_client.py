import socket

HOST = '10.42.0.21'
PORT = 1337

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Moin, Meister')
    data = s.recv(1024)

print("recieved", repr(data))