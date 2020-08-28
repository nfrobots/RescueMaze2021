#pragma once

#include "ASL/types.h"

constexpr int ANALOG_SENSOR_SMOOTHNESS = 5;

class AnalogSensor
{
public:
    AnalogSensor(asl::uint8_t pin);
    void update();
    int getValue();
    int getRawValue();

    int value = 0; //smoothed value

private:
    asl::uint8_t pin;
    int values[ANALOG_SENSOR_SMOOTHNESS];
    asl::uint8_t index = 0;
    int total = 0;
};


struct RGBAValue
{
    RGBAValue(unsigned int red, unsigned int green, unsigned int blue, unsigned int alpha);
    RGBAValue();
    unsigned int red, green, blue, alpha;
};

constexpr int COLOR_SENSOR_SMOOTHNESS = 5;

class ColorSensor
{
public:
    ColorSensor(asl::uint8_t outPin, asl::uint8_t s0Pin, asl::uint8_t s1Pin, asl::uint8_t s2Pin, asl::uint8_t s3pin);
    void update();
    RGBAValue getValue();
    RGBAValue getRawValue();

    RGBAValue value; //smoothed value
private:
    asl::uint8_t outPin;
    asl::uint8_t s2Pin;
    asl::uint8_t s3Pin;
    RGBAValue values[COLOR_SENSOR_SMOOTHNESS];
    asl::uint8_t index = 0;
    RGBAValue total;
};


constexpr int ROTATION_SENSOR_SMOOTHNESS = 5;



class RotationSensor
{
public:
    RotationSensor();
    void update();

    asl::int16_t accelerometerX;
    asl::int16_t accelerometerY;
    asl::int16_t accelerometerZ;
    asl::int16_t temperature;
    asl::int16_t gyroscopeX;
    asl::int16_t gyroscopeY;
    asl::int16_t gyroscopeZ;

private:
};
