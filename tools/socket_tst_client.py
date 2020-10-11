import socket

# HOST = '10.42.0.21'
HOST = '192.168.178.48'
PORT = 1337

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        print(s.recv(1024))

print("closed")