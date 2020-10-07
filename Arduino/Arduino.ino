#include "Transmitter.h"
#include "Devices.h"

#include <Arduino.h>
#include <Wire.h>
#include "MPU6050_6Axis_MotionApps20.h"

AnalogSensor irSensors[8] = {
    AnalogSensor(A7),
    AnalogSensor(A8),
    AnalogSensor(A9),
    AnalogSensor(A10),
    AnalogSensor(A11),
    AnalogSensor(A12),
    AnalogSensor(A13),
    AnalogSensor(A14)
};

AnalogSensor longDistanceIRSensor(A15);

ColorSensor colorSensor(49, 50, 51, 52, 53);

MPU6050 mpu;
uint8_t fifoBuffer[42]; // FIFO storage buffer
Quaternion q;


Transmitter t(
    JSON_TR_PARSER_READABLE,
    TrValue("LIR", longDistanceIRSensor.value),
    TrValue("IR0", irSensors[0].value),
    TrValue("IR1", irSensors[1].value),
    TrValue("IR2", irSensors[2].value),
    TrValue("IR3", irSensors[3].value),
    TrValue("IR4", irSensors[4].value),
    TrValue("IR5", irSensors[5].value),
    TrValue("IR6", irSensors[6].value),
    TrValue("IR7", irSensors[7].value),
    TrValue("GYX", q.x),
    TrValue("GYY", q.y),
    TrValue("GYZ", q.z),
    TrValue("RED", colorSensor.value.red),
    TrValue("GRE", colorSensor.value.green),
    TrValue("BLU", colorSensor.value.blue),
    TrValue("ALP", colorSensor.value.alpha)
);

int8_t setupSuccess = 0; // 0 -> sucessful

void setup() {
    Wire.begin();
    Wire.setClock(400000);

    Serial.begin(9600);

    mpu.initialize();
    int status = mpu.dmpInitialize();

    // supply your own gyro offsets here, scaled for min sensitivity
    mpu.setXGyroOffset(-9);
    mpu.setYGyroOffset(-95);
    mpu.setZGyroOffset(34);
    mpu.setXAccelOffset(-2987);
    mpu.setYAccelOffset(835);
    mpu.setZAccelOffset(1005);

    if (status == 0)  //init succesfull
    {
        mpu.CalibrateAccel(6);
        mpu.CalibrateGyro(6);
        mpu.setDMPEnabled(true);
    }
    else
    {
        Serial.print(F("DMP Initialization failed"));
        setupSuccess = 1;
    }
}

void loop() {
    if (setupSuccess != 0) return;

    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) // Get the Latest packet
    { 
        mpu.dmpGetQuaternion(&q, fifoBuffer); //write it to the quaternion
    }

    longDistanceIRSensor.update();
    colorSensor.update();

    for(int i = 0; i < 8; i++)
    {
        irSensors[i].update();
    }

    t.transmitt();
    delay(10);
}