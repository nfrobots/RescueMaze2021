/**
 * CAREFUL! YOU HAVE FULL CONTROLL ON UPDATING VALUES. 
 * YOU HAVE TO CALL THE UPDATE FUNCTION EXPLICITLY.
 * EVEN GETVALUE FUNCTION DOES NOT UPDATE THEM.
 * IT WILL INSTEAD RETURN THE VALUE FROM THE MOST RECENT UPDATE() CALL.
*/

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