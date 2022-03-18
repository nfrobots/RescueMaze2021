from serial import Serial


def constrain(v, min, max):
    if v < min:
        return min
    elif v > max:
        return max
    else:
        return v

def generate_motor_instruction_string(m1, m2, m3, m4):
    """Generates bytes representing motor instructions.
    Motor values have to be in the range of a signed short: [-32768, 32767]"""

    out = b"m"
    m1 = constrain(m1, -32768, 32767)
    m2 = constrain(m2, -32768, 32767)
    m3 = constrain(m3, -32768, 32767)
    m4 = constrain(m4, -32768, 32767)
    return out + m1.to_bytes(2, 'big', signed=True) + m2.to_bytes(2, 'big', signed=True) \
               + m3.to_bytes(2, 'big', signed=True) + m4.to_bytes(2, 'big', signed=True)


if __name__ == "__main__":
    print(len(generate_motor_instruction_string(600, 600, 600, 600)))
    print(generate_motor_instruction_string(600, 600, 600, 600))

    serial = Serial()