import socket
import json
import time

HOST = '10.42.0.21'
# HOST = '192.168.178.48'
PORT = 1337

connected = False
connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect():
    connection.connect((HOST, PORT))
    global connected
    connected = True

def request_data():
    if not connected:
        return {"moin": 1, "Meister": 1}
    connection.send(b'd')
    data_bytes = connection.recv(1024)
    return json.loads(data_bytes.decode('utf-8'))

def request_calibration(value_string):
    if not connected:
        return
    connection.send(b'c' + value_string.encode("utf-8"))

def request_led_color(r, g, b):
    if not connected:
        return
    connection.send("l{} {} {}".format(r, g, b).encode("utf-8"))

def close_connection():
    if not connected:
        return
    print("rofl")
    connection.send(b'q')
    print("hrrrr")
    connection.close()

if __name__ == "__main__":
    while True:
        #msg = request_data_bytes().decode('utf-8')
        
        print(request_data())
        time.sleep(1)