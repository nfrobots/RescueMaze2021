#include "asl/types.h"


volatile byte oldPinInput = 0;
volatile long _encoder_count[4] = {0};


// this is truly a magic function. Only god remembers how it works...
ISR(PCINT2_vect)
{
    // get pins from port k (analog pins 8 - 15 i guess)
    byte newPinInput = PINK; // pink is a colour, innit? nah its PIN-K

    for (byte i = 0; i < 4; i++)
    {
        // mask out two bits
        byte maskedOldPinInput = (oldPinInput & (0b11 << 2 * i)) >> 2 * i;
        byte maskedNewPinInput = (newPinInput & (0b11 << 2 * i)) >> 2 * i;

        // the transition is only valid if the xor product is 1 or 2
        byte validation = maskedNewPinInput ^ maskedOldPinInput;
        if (validation == 1 || validation == 2)
        {
            // determine rotation direction by using the bitmask 0b01100110
            if ((1 << ((maskedOldPinInput << 1) | (maskedNewPinInput >> 1))) & 0b01100110)
            {
                _encoder_count[i]++;
            }
            else
            {
                _encoder_count[i]--;
            }
        }
    }

    oldPinInput = newPinInput;
}



// RL M 1 , hinten links --  code [3], LOW
#define NMS_M1_SPEED 3
#define NMS_M1_DIREC 2
#define NMS_M1_INDEX 3
#define NMS_M1_FORWARD LOW


// RL M 2, hinten rechts -- code [0], HIGH
#define NMS_M2_SPEED 5
#define NMS_M2_DIREC 4
#define NMS_M2_INDEX 2
#define NMS_M2_FORWARD HIGH


// RL M 3 , vorne links -- code [1], HIGH
#define NMS_M3_SPEED 9
#define NMS_M3_DIREC 8
#define NMS_M3_INDEX 1
#define NMS_M3_FORWARD HIGH


//  RL M 4 , vorne rechts -- code [2], LOW
#define NMS_M4_SPEED 7
#define NMS_M4_DIREC 6
#define NMS_M4_INDEX 0
#define NMS_M4_FORWARD LOW



enum class NMS_MOTOR
{
    BACK_LEFT = 1,
    M1 = 1,
    BACK_RIGHT = 2,
    M2 = 2,
    FRONT_LEFT = 3,
    M3 = 3,
    FRONT_RIGHT = 4,
    M4 = 4
};

class MotorManager
{
public:
    void begin()
    {
        // PinModes for H-Bridges
        pinMode(NMS_M1_SPEED, OUTPUT);
        pinMode(NMS_M1_DIREC, OUTPUT);
        pinMode(NMS_M2_SPEED, OUTPUT);
        pinMode(NMS_M2_DIREC, OUTPUT);
        pinMode(NMS_M3_SPEED, OUTPUT);
        pinMode(NMS_M3_DIREC, OUTPUT);
        pinMode(NMS_M4_SPEED, OUTPUT);
        pinMode(NMS_M4_DIREC, OUTPUT);


        // PinModes for Encoder
        pinMode(A8, INPUT_PULLUP);
        pinMode(A9, INPUT_PULLUP);
        pinMode(A10, INPUT_PULLUP);
        pinMode(A11, INPUT_PULLUP);
        pinMode(A12, INPUT_PULLUP);
        pinMode(A13, INPUT_PULLUP);
        pinMode(A14, INPUT_PULLUP);
        pinMode(A15, INPUT_PULLUP);

        PCICR |= 1 << PCIE2;
        PCMSK2 |= 0xFF;
    }

    void setMotorSpeed(NMS_MOTOR motor, int speed)
    {
        asl::uint8_t forward = speed > 0 ? 1 : 0;
        asl::uint8_t _speed = abs(speed);
        _speed = constrain(_speed, 0, 255);
        switch (motor)
        {
        case NMS_MOTOR::BACK_LEFT:
            if (_speed != 0) digitalWrite(NMS_M1_DIREC, forward ? NMS_M1_FORWARD : !NMS_M1_FORWARD);
            analogWrite(NMS_M1_SPEED, _speed);
            break;
        case NMS_MOTOR::BACK_RIGHT:
            if (_speed != 0) digitalWrite(NMS_M2_DIREC, forward ? NMS_M2_FORWARD : !NMS_M2_FORWARD);
            analogWrite(NMS_M2_SPEED, _speed);
            break;
        case NMS_MOTOR::FRONT_LEFT:
            if (_speed != 0) digitalWrite(NMS_M3_DIREC, forward ? NMS_M3_FORWARD : !NMS_M3_FORWARD);
            analogWrite(NMS_M3_SPEED, _speed);
            break;
        case NMS_MOTOR::FRONT_RIGHT:
            if (_speed != 0) digitalWrite(NMS_M4_DIREC, forward ? NMS_M4_FORWARD : !NMS_M4_FORWARD);
            analogWrite(NMS_M4_SPEED, _speed);
            break;
        }
    }

    long getEncoder(NMS_MOTOR motor)
    {
        // switch (motor)
        // {
        //     case NMS_MOTOR::BACK_LEFT:
        //     return _encoder_count[NMS_M1_INDEX];
        //     case NMS_MOTOR::BACK_RIGHT:
        //     return _encoder_count[NMS_M2_INDEX];
        //     case NMS_MOTOR::FRONT_LEFT:
        //     return _encoder_count[NMS_M3_INDEX];
        //     case NMS_MOTOR::FRONT_RIGHT:
        //     return _encoder_count[NMS_M4_INDEX];
        // }
        return _encoder_count[motorToIndex(motor)];
    }

    void moveMotor(NMS_MOTOR motor, long amount)
    {
        asl::uint8_t motorIndex = motorToIndex(motor);
        targets[motorToIndex(motor)] = getEncoderCount(motor) + amount; 
    }

    void update()
    {
        for(asl::uint8_t i = 1; i <= 4; i++)
        {
            NMS_MOTOR motor = static_cast<NMS_MOTOR>(i);
            asl::uint8_t motorIndex = motorToIndex(motor);
            long diff = targets[motorIndex] - getEncoderCount(motor);
            int speed = map(diff, -100, 100, -255, 255);
            if (speed > 40 || speed < -40)
            {
                speed = constrain(speed, -255, 255);
                setMotorSpeed(motor, speed);
            }
            else
            {
                setMotorSpeed(motor, 0);
            }
            Serial.print("Motor "); Serial.print(i); Serial.print(": "); Serial.print(diff); Serial.print(" "); Serial.println(speed);
        } 
    }

private:
    long targets[4] = {0, 0, 0, 0};

    asl::uint8_t motorToIndex(NMS_MOTOR motor)
    {
        switch (motor)
        {
            case NMS_MOTOR::BACK_LEFT:
            return 3;
            case NMS_MOTOR::BACK_RIGHT:
            return 2;
            case NMS_MOTOR::FRONT_LEFT:
            return 1;
            case NMS_MOTOR::FRONT_RIGHT:
            return 0;
        }
    }

    long getEncoderCount(NMS_MOTOR motor)
    {
        switch (motor)
        {
            case NMS_MOTOR::BACK_LEFT:
            return _encoder_count[3];
            case NMS_MOTOR::BACK_RIGHT:
            return -_encoder_count[2];
            case NMS_MOTOR::FRONT_LEFT:
            return _encoder_count[1];
            case NMS_MOTOR::FRONT_RIGHT:
            return -_encoder_count[0];
        }
    }
};
