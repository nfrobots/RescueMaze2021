#include "Transmitter.h"
#include "Devices.h"

IrSensor s(A6);

int gbl_a = 3;
float gbl_b = 235.32f;

JsonTransmitter t (
    JSON_TR_PARSER_DEFAULT,
    TrValue<int>("IrVak", s.value),
    TrValue<float>("gbl", gbl_b)
);


void setup()
{
    Serial.begin(9600);
}

void loop()
{
    s.update();
    t.transmitt();
}