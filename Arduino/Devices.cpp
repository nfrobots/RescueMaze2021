#include "Devices.h"

#include <Arduino.h>

AnalogSensor::AnalogSensor(asl::uint8_t pin) : pin(pin)
{

    for(int i = 0; i < ANALOG_SENSOR_SMOOTHNESS; i++)
    {
        update();
    }
}

void AnalogSensor::update()
{
    total -= values[index];
    values[index] = getRawValue();
    total += values[index];
    int temp = (++index) % ANALOG_SENSOR_SMOOTHNESS;
    index = temp;
    value = total / ANALOG_SENSOR_SMOOTHNESS;
}

int AnalogSensor::getValue()
{
    return value;
}

int AnalogSensor::getRawValue()
{
    return analogRead(pin);
}


RGBAValue::RGBAValue(unsigned int red, unsigned int green, unsigned int blue, unsigned int alpha)
    : red(red), green(green), blue(blue), alpha(alpha) {};

RGBAValue::RGBAValue()
    : red(0), green(0), blue(0), alpha(0) {};


ColorSensor::ColorSensor(asl::uint8_t outPin, asl::uint8_t s0Pin, asl::uint8_t s1Pin, asl::uint8_t s2Pin, asl::uint8_t s3Pin)
    : outPin(outPin), s2Pin(s2Pin), s3Pin(s3Pin)
{
    pinMode(s0Pin, OUTPUT);
    pinMode(s1Pin, OUTPUT);
    pinMode(s2Pin, OUTPUT);
    pinMode(s3Pin, OUTPUT);
    pinMode(outPin, INPUT);

    //set freq
    digitalWrite(s0Pin, HIGH);
    digitalWrite(s1Pin, LOW);

    for (int i = 0; i < COLOR_SENSOR_SMOOTHNESS; i++)
    {
        update();
    }
}

void ColorSensor::update()
{
    total.red -= values[index].red;
    total.green -= values[index].green;
    total.blue -= values[index].blue;
    total.alpha -= values[index].alpha;

    values[index] = getRawValue();

    total.red += values[index].red;
    total.green += values[index].green;
    total.blue += values[index].blue;
    total.alpha += values[index].alpha;

    int temp = (++index) % COLOR_SENSOR_SMOOTHNESS;
    index = temp;
    
    value.red = total.red / COLOR_SENSOR_SMOOTHNESS;
    value.green = total.green / COLOR_SENSOR_SMOOTHNESS;
    value.blue = total.blue / COLOR_SENSOR_SMOOTHNESS;
    value.alpha = total.alpha / COLOR_SENSOR_SMOOTHNESS;
}

RGBAValue ColorSensor::getValue()
{
    return value;
}

RGBAValue ColorSensor::getRawValue()
{
    //Red
    digitalWrite(s2Pin, LOW);
    digitalWrite(s3Pin, LOW);
    int r = pulseIn(outPin, LOW, 500);

    //Clear
    digitalWrite(s2Pin, HIGH);
    digitalWrite(s3Pin, LOW);
    int a = pulseIn(outPin, LOW, 500);

    //Green
    digitalWrite(s2Pin, HIGH);
    digitalWrite(s3Pin, HIGH);
    int g = pulseIn(outPin, LOW, 500);

    //Blue
    digitalWrite(s2Pin, LOW);
    digitalWrite(s3Pin, HIGH);
    int b = pulseIn(outPin, LOW, 500);

    return RGBAValue(r, g, b, a);
}