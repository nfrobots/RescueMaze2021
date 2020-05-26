#pragma once

#include "ASL/types.h"

#define IRSM 5

class IrSensor
{
public:
    IrSensor(asl::uint8_t pin);
    void update();
    int getValue();
    int getRawValue();

private:
    asl::uint8_t pin;
    int values[IRSM];
    asl::uint8_t index = 0;
    int total = 0;
};

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
}

int IrSensor::getValue()
{
    return total / IRSM;
}

int IrSensor::getRawValue()
{
    return analogRead(pin);
}