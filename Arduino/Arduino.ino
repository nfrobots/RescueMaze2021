#include "Transmitter.h"
#include "Devices.h"
#include "ASL/types.h"
#include "MotorManager.h"

#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include "MPU6050_6Axis_MotionApps20.h"
#include "VL53L0X.h"
#include "Adafruit_MLX90614.h"
#include "Adafruit_SSD1306.h"


#define TCA_ADDRESS 0x70
#define VLX_ADDRESS 0x29
#define MPU_ADDRESS 0x68
#define MLX_ADDRESS 0x5a

#define MLX_RIGHT_BUS 0
#define MLX_LEFT_BUS 1
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

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32

#define OLED_RESET     -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

bool mainSwitch = false;

long motorEncoders[4] = {0};

Servo rkds;

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
    TrValue("TML", mlxLeftTemp),
    TrValue("TMR", mlxRightTemp),
    TrValue("M1E", motorEncoders[0]),
    TrValue("M2E", motorEncoders[1]),
    TrValue("M3E", motorEncoders[2]),
    TrValue("M4E", motorEncoders[3]),
    TrValue("SWI", mainSwitch)
);

void tcaSelectBus(asl::uint8_t bus)
{
    if (bus > 7) return;

    Wire.beginTransmission(TCA_ADDRESS);
    Wire.write(1 << bus);
    Wire.endTransmission();
    delay(1);
}

int initializeVlxs()
{
    for (int i = 0; i < 8; i++)
    {
        if (i == 5) continue;
        tcaSelectBus(i);
        delay(10);
        if(!vlx.init())
            return -1 - i;
        vlx.startContinuous(100);
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

void dropKit()
{
    rkds.attach(41, 500, 2400);
    rkds.write(60);
    delay(500);
    rkds.write(0);
    delay(200);
    rkds.detach();
}

void setup()
{
    Serial.begin(9600);

    Serial.println(F("[INFO] starting init"));

    delay(50);

    Wire.begin();
    motorManager.begin();

    if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
        Serial.println(F("SSD1306 allocation failed"));
        for(;;);
    }

    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);
    display.setTextSize(1);
    display.println(F("[INFO] starting init"));
    display.display();


    //int error = initializeMpu();
    //if (error != 0)
    //{
    //    Serial.print(F("[ERROR] Failed to initialize Mpu"));
    //    while (true) {}
    //}

    delay(200);

    int error = initializeVlxs();
    if (error != 0)
    {
        Serial.print(F("[ERROR] Failed to initialize Vlxs. Error Code: "));
        Serial.println(error);
        while (true) {}
    }


    error = initializeMlxs();
    if (error != 0)
    {
        Serial.print(F("[ERROR] Failed to initialize Mlxs"));
        while (true) {}
    }

    pinMode(27, INPUT_PULLUP);

    Serial.print(F("[OK] Setup succesfull\n"));


    display.println(F("[OK] init successfull"));
    display.display();
    delay(200);
    display.clearDisplay();
    display.display();

    //motorManager.moveMotor(NMS_MOTOR::BACK_RIGHT, 520);
    //motorManager.moveMotor(NMS_MOTOR::FRONT_RIGHT, 520);
    //motorManager.moveMotor(NMS_MOTOR::BACK_LEFT, -520);
    //motorManager.moveMotor(NMS_MOTOR::FRONT_LEFT, -520);
}

void loop()
{
    motorManager.update();
//    tcaSelectBus(MPU_BUS);
//    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer))
//    { 
//        mpu.dmpGetQuaternion(&q, fifoBuffer);
//    }

    for (int i = 0; i < 8; i++)
    {
        if (i == 5) continue;
        tcaSelectBus(i);
        vlxData[i] = vlx.readRangeContinuousMillimeters();
        delay(1);
    }

    tcaSelectBus(MLX_LEFT_BUS);
    mlxLeftTemp = mlx.readObjectTempC();

    tcaSelectBus(MLX_RIGHT_BUS);
    mlxRightTemp = mlx.readObjectTempC();

    greyScaleSensor.update();

    mainSwitch = digitalRead(27);

    motorEncoders[0] = motorManager.getEncoder(NMS_MOTOR::M1);
    motorEncoders[1] = motorManager.getEncoder(NMS_MOTOR::M2);
    motorEncoders[2] = motorManager.getEncoder(NMS_MOTOR::M3);
    motorEncoders[3] = motorManager.getEncoder(NMS_MOTOR::M4);

    if (Serial.available())
    {
        char incomeing_byte = Serial.read();
        if (incomeing_byte == 'd')
        {
            t.transmitt();
            display.clearDisplay();
            display.print("-");

            display.display();
            if(display.getCursorX() > 60)
            {
                display.setCursor(10, 10);
            }
        }
        else if (incomeing_byte == 'm')
        {
            for (int i = 1; i <= 4; i++)
            {
                asl::int16_t value = (Serial.read() << 8) | Serial.read();
                motorManager.moveMotor(static_cast<NMS_MOTOR>(i), value);
            }
        }
        else if(incomeing_byte == 'k')
        {
            display.print("KIT");
            display.display();
            dropKit();
            display.clearDisplay();
        }
    }
}
