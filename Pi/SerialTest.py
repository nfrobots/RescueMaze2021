
import serial
from time import sleep

serial_connection = serial.Serial('/dev/ttyACM0', 9600, timeout=3)


while True:
    print(serial_connection.in_waiting)

    print(serial_connection.read(8))
