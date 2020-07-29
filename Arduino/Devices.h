#pragma once

#include "ASL/types.h"

constexpr int IRSM = 5;

class IrSensor
{
public:
    IrSensor(asl::uint8_t pin);
    void update();
    int getValue();
    int getRawValue();

    int value = 0; //smoothed value
private:
    asl::uint8_t pin;
    int values[IRSM];
    asl::uint8_t index = 0;
    int total = 0;
};

struct RGBAValue
{
    RGBAValue(unsigned int red, unsigned int green, unsigned int blue, unsigned int alpha);
    RGBAValue();
    unsigned int red, green, blue, alpha;
};

constexpr int CSM = 5;

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
    RGBAValue values[CSM];
    asl::uint8_t index = 0;
    RGBAValue total;
};