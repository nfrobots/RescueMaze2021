#pragma once

#include "ASL/types.h"

const int IRSM = 5;

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
    int value = 0; //smoothed value
};