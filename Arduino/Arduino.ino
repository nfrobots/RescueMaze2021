#include "Transmitter.h"
#include "Devices.h"
#include "ASL/types.h"
#include "MotorManager.h"

#include <Arduino.h>
#include <Wire.h>
#include "MPU6050_6Axis_MotionApps20.h"
#include "VL53L0X.h"
#include "Adafruit_MLX90614.h"


#define TCA_ADDRESS 0x70
#define VLX_ADDRESS 0x29
#define MPU_ADDRESS 0x68
#define MLX_ADDRESS 0x5a

#define MLX_LEFT_BUS 0
#define MLX_RIGHT_BUS 1
#define MPU_BUS 2

MotorManager motorManager;

VL53L0X vlx;
asl::uint16_t vlxData[8] = {0};

MPU6050 mpu;
uint8_t fifoBuffer[42]; // FIFO storage buffer
Quaternion q;

AnalogSensor greyScaleSensor(A6);

Adafruit_MLX90614 mlx;
double mlxLeftTemp = 0;
double mlxRightTemp = 0;


Transmitter t (
    JSON_TR_PARSER_REDUCED,
    TrValue("IR0", vlxData[0]),
    TrValue("IR1", vlxData[1]),
    TrValue("IR2", vlxData[2]),
    TrValue("IR3", vlxData[3]),
    TrValue("IR4", vlxData[4]),
    TrValue("IR5", vlxData[5]),
    TrValue("IR6", vlxData[6]),
    TrValue("IR7", vlxData[7]),
    TrValue("GYX", q.x),
    TrValue("GYY", q.y),
    TrValue("GYZ", q.z),
    TrValue("GRS", greyScaleSensor.value),
    TrValue("TLA", mlxLeftTemp),
    TrValue("TMR", mlxRightTemp)
);

void tcaSelectBus(asl::uint8_t bus)
{
    if (bus > 7) return;

    Wire.beginTransmission(TCA_ADDRESS);
    Wire.write(1 << bus);
    Wire.endTransmission();
}

int initializeVlxs()
{
    for (int i = 0; i < 8; i++)
    {
        tcaSelectBus(i);
        if(!vlx.init())
            return -1;
        vlx.startContinuous();
    }
    return 0;
}

int initializeMpu()
{
    tcaSelectBus(MPU_BUS);
    mpu.initialize();
    int status = mpu.dmpInitialize();

    mpu.setXGyroOffset(-9);
    mpu.setYGyroOffset(-95);
    mpu.setZGyroOffset(34);
    mpu.setXAccelOffset(-2987);
    mpu.setYAccelOffset(835);
    mpu.setZAccelOffset(1005);

    if (status != 0)  // some error
    {
        return -1;
    }

    mpu.CalibrateAccel(6);
    mpu.CalibrateGyro(6);
    mpu.setDMPEnabled(true);
    return 0;
}

int initializeMlxs()
{
    tcaSelectBus(MLX_LEFT_BUS);
    if (!mlx.begin())
        return -1;
    
    tcaSelectBus(MLX_RIGHT_BUS);
    if (!mlx.begin())
        return -1;

    return 0;
}

void setup()
{
    Wire.begin();
    Wire.setClock(400000);
    motorManager.begin();
    Serial.begin(9600);

    int error = initializeMpu();
    if (error != 0)
    {
        Serial.print(F("[ERROR] Failed to initialize Mpu"));
        while (true) {}
    }

    error = initializeVlxs();
    if (error != 0)
    {
        Serial.print(F("[ERROR] Failed to initialize Vlxs"));
        while (true) {}
    }

    error = initializeMlxs();
    if (error != 0)
    {
        Serial.print(F("[ERROR] Failed to initialize Mlxs"));
        while (true) {}
    }

    Serial.print(F("[OK] Setup succesfull\n"));

    motorManager.moveMotor(NMS_MOTOR::BACK_RIGHT, 500);
}

void loop()
{
    motorManager.update();
    tcaSelectBus(MPU_BUS);
    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer))
    { 
        mpu.dmpGetQuaternion(&q, fifoBuffer);
    }

    for (int i = 0; i < 8; i++)
    {
        tcaSelectBus(i);
        vlxData[i] = vlx.readRangeContinuousMillimeters();
    }

    tcaSelectBus(MLX_LEFT_BUS);
    mlxLeftTemp = mlx.readObjectTempC();

    tcaSelectBus(MLX_RIGHT_BUS);
    mlxRightTemp = mlx.readObjectTempC();

    greyScaleSensor.update();

    if (Serial.available())
    {
        char incomeing_byte = Serial.read();
        if (incomeing_byte == 'd')
        {
            t.transmitt();
        }
    }
    delay(1);
}