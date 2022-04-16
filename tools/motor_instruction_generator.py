import time
import serial

def constrain(value, min_, max_):
    """just like the arduino constrain, except it's not a macro"""
    if value < min_:
        return min_
    elif value > max_:
        return max_
    else:
        return value

def generate_motor_instruction_string(m1: int, m2: int, m3: int, m4: int):
    """Generates bytes representing motor instructions.
    Motor values have to be in the range of a signed short: [-32768, 32767]"""

    out = b"m"
    m1 = constrain(m1, -32768, 32767)
    m2 = constrain(m2, -32768, 32767)
    m3 = constrain(m3, -32768, 32767)
    m4 = constrain(m4, -32768, 32767)
    return out + m1.to_bytes(2, 'big', signed=True) + m2.to_bytes(2, 'big', signed=True) \
               + m3.to_bytes(2, 'big', signed=True) + m4.to_bytes(2, 'big', signed=True)

turn_right_instruction  = generate_motor_instruction_string(520, -520, 520, -520)
turn_left_instruction   = generate_motor_instruction_string(-520, 520, -520, 520)
forward_instruction     = generate_motor_instruction_string(790, 790, 790, 790)
backward_instruction    = generate_motor_instruction_string(-790, -790, -790, -790)

if __name__ == "__main__":
    print(len(generate_motor_instruction_string(600, 600, 600, 600)))
    print(generate_motor_instruction_string(600, 600, 600, 600))


    serial_connection = serial.Serial("/dev/ttyACM0", 9600, timeout=0.2)

    time.sleep(5)

    while serial_connection.in_waiting < 22:
        print("[INFO] waiting for Arduino to finish initialization and establish serial connection")
        time.sleep(0.5)
    
    try:
        setup_info = serial_connection.read(1024).decode('utf-8')
    except UnicodeDecodeError:
        print("[ERROR] could not decode setup info")
        setup_info = "[ERROR]"

    if "[ERROR]" in setup_info:
        print("[ERROR] connecting to Arduino failed")
    else:
        print(f"[OK] serial connection established with info: '{setup_info}'")
        connected = True


    serial_connection.write(forward_instruction)
    time.sleep(5)
    serial_connection.write(turn_left_instruction)
    time.sleep(3)
    serial_connection.write(turn_right_instruction)
    time.sleep(3)
    serial_connection.write(backward_instruction)

    print(serial_connection.read(1024))
