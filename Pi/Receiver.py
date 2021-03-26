import serial
import time
import json

print("[INFO] INITIALIZING SERIAL RECEIVER")

REQUEST_BYTE = 'd'.encode('utf-8')

serial_connection = serial.Serial('/dev/ttyACM0', 9600, timeout=0.2)

while serial_connection.in_waiting == 0:
    print("[INFO] WAITING FOR ARDUINO TO FINISH INITIALIZATION AND ESTABLISH SERIAL CONNETION")
    time.sleep(0.5)

try:
    setup_info = serial_connection.read(1024).decode("utf-8")
except UnicodeDecodeError:
    print("could not decode setup info")
    setup_info = "|DECODE ERROR|"


if "[ERROR]" in setup_info:
    print("SHIIT BRUH")
    exit()

print(f"[OK] SERIAL CONNECTION ESTABLISHED WITH: {setup_info}")

def request_data_bytes():
    """Requests data from arduino and returns it as a bytes or None if error occured"""
    serial_connection.write(REQUEST_BYTE)
    data = b''
    incomeing_char = serial_connection.read()

    if incomeing_char == b'': # serial_connection.read() resulted in time-out
        print("serial read timed out")
        return None

    while incomeing_char != b'}':
        data += incomeing_char
        incomeing_char = serial_connection.read()

    try:
        return data + b'}'
    except UnicodeDecodeError:
        print("error occured while decodeing unicode character received from arduino")
        return None

def get_data():
    """Requests data from Arduino and returns it as python dict. Returns None if error occured"""
    data_string = request_data_bytes().decode('utf-8')
    if not data_string: # error occured in request_data_string()
        return None
    try:
        data_json = json.loads(data_string)
        return data_json
    except json.decoder.JSONDecodeError:
        print("error occured while decoding json string")
        
def get_data_s():
    data = get_data()
    while get_data == None:
        print("get_data_s: get_data failed!")
        data = get_data()
    return data

if __name__ == "__main__":
    for _ in range(100):
        print(get_data()["IR0"])
        time.sleep(1)
        