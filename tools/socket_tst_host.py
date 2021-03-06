import socket

# HOST = '10.42.0.21'
HOST = '192.168.178.48'
PORT = 1337

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(5)
    s.bind((HOST, PORT))
    s.listen()
    try:
        conn, addr = s.accept()
    except socket.timeout:
        print("connection timeout")
        exit()
        
    with conn:
        conn.recv(1024)

print("closed")