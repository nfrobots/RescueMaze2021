import serial
import json

ser = serial.Serial("/dev/ttyACM0", 9600)

while True:
    msg = ""
    incomeing_char = ""
    while incomeing_char != "}":
        try:
            incomeing_char = ser.read(1).decode("utf-8")
        except ValueError:
            break
        
        msg += incomeing_char


    try:
        sensor_data = json.loads(msg)

        print("IR0", sensor_data["IR0"] // 10 * '#')
        print("IR1", sensor_data["IR1"] // 10 * '#')
        print("IR2", sensor_data["IR2"] // 10 * '#')
        print("IR3", sensor_data["IR3"] // 10 * '#')
        print("IR4", sensor_data["IR4"] // 10 * '#')
        print("IR5", sensor_data["IR5"] // 10 * '#')
        print("IR6", sensor_data["IR6"] // 10 * '#')
        print("IR7", sensor_data["IR7"] // 10 * '#')

    except json.JSONDecodeError:
        pass