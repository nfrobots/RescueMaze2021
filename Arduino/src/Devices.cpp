#include "Devices.h"

#include <Arduino.h>

IrSensor::IrSensor(asl::uint8_t pin) : pin(pin)
{
    for(int i = 0; i < IRSM; i++)
    {
        update();
    }
}

void IrSensor::update()
{
    total -= values[index];
    values[index] = getRawValue();
    total += values[index];
    index = ++index % IRSM;
    value = total / IRSM;
}

int IrSensor::getValue()
{
    return value;
}

int IrSensor::getRawValue()
{
    return analogRead(pin);
}