#include <Arduino.h>
// #include <Wire.h>

// constexpr int GYROSCOPE_ADDRESS = 0x68;

// int16_t accelerometerX, accelerometerY, accelerometerZ, temperature, gyroscopeX, gyroscopeY, gyroscopeZ;

// void setup()
// {
//     Serial.begin(9600);
//     Wire.begin();
//     Wire.beginTransmission(GYROSCOPE_ADDRESS);
//     Wire.write(0x68);
//     Wire.write(0);
//     Wire.endTransmission(true);
// }

// void loop()
// {
//     Wire.beginTransmission(GYROSCOPE_ADDRESS);
//     Wire.write(0x3B);
//     Wire.endTransmission(false);
//     Wire.requestFrom(GYROSCOPE_ADDRESS, 14, true);
//     accelerometerX  = Wire.read() << 8 | Wire.read(); // 0x3B and 0x3C
//     accelerometerY  = Wire.read() << 8 | Wire.read(); // 0x3D and 0x3E
//     accelerometerZ  = Wire.read() << 8 | Wire.read(); // 0x3F and 0x40
//     temperature     = Wire.read() << 8 | Wire.read(); // 0x41 and 0x42
//     gyroscopeX      = Wire.read() << 8 | Wire.read(); // 0x43 and 0x44
//     gyroscopeY      = Wire.read() << 8 | Wire.read(); // 0x45 and 0x46
//     gyroscopeZ      = Wire.read() << 8 | Wire.read(); // 0x47 and 0x48

//     Serial.print("AcX = ");     Serial.print(accelerometerX);
//     Serial.print(" | AcY = ");  Serial.print(accelerometerY);
//     Serial.print(" | AcZ = ");  Serial.print(accelerometerZ);
//     Serial.print(" | Tmp = ");  Serial.print(temperature/340.00+36.53);  //equation for temperature in degrees C from datasheet
//     Serial.print(" | GyX = ");  Serial.print(gyroscopeX);
//     Serial.print(" | GyY = ");  Serial.print(gyroscopeY);
//     Serial.print(" | GyZ = ");  Serial.print(gyroscopeZ);
//     Serial.println();
//     delay(100);
// }


#include "Transmitter.h"
#include "Devices.h"

int a = 3;

AnalogSensor irSensors[8] = {
    AnalogSensor(A6),
    AnalogSensor(A7),
    AnalogSensor(A8),
    AnalogSensor(A9),
    AnalogSensor(A10),
    AnalogSensor(A11),
    AnalogSensor(A12),
    AnalogSensor(A13),
};

AnalogSensor longDistanceIRSensor(A14);

Transmitter t(
    JSON_TR_PARSER_REDUCED,
    TrValue("LDIR", longDistanceIRSensor.value),
    TrValue("IR0", irSensors[0].value),
    TrValue("IR1", irSensors[1].value),
    TrValue("IR2", irSensors[2].value),
    TrValue("IR3", irSensors[3].value),
    TrValue("IR4", irSensors[4].value),
    TrValue("IR5", irSensors[5].value),
    TrValue("IR6", irSensors[6].value),
    TrValue("IR7", irSensors[7].value)
);


void setup()
{
    Serial.begin(9600);
}

void loop()
{
    longDistanceIRSensor.update();
    for(int i = 0; i < 8; i++)
    {
        irSensors[i].update();
    }
    t.transmitt();
    delay(100);
}