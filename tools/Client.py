import socket
import json
import time

HOST = '10.42.0.21'
# HOST = '192.168.178.48'
PORT = 1337

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect((HOST, PORT))

def request_data():
    connection.send(b'd')
    data_bytes = connection.recv(1024)
    return json.loads(data_bytes.decode('utf-8'))

def close_connection():
    print("rofl")
    connection.send(b'q')
    print("hrrrr")
    connection.close()

if __name__ == "__main__":
    while True:
        #msg = request_data_bytes().decode('utf-8')
        
        print(request_data())
        time.sleep(1)