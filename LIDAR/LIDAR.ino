

#include <Wire.h>
#include <VL53L1X.h>

VL53L1X sensor;


enum class LidarDirection
{
  BACK = 0,
  RIGHT = 1,
  FRONT = 2,
  LEFT = 3,
};

volatile unsigned long prev_fall;
volatile bool r = false;

volatile unsigned char prevPortB;
volatile unsigned char changeBit;

volatile unsigned short delta;
volatile LidarDirection state;

volatile short avgTimes[4] = {500, 500, 500, 500};

ISR(PCINT0_vect)
{
  unsigned char portB = PINB & 0b00000011;
  changeBit = (portB ^ prevPortB);
  prevPortB = portB;

  if ((portB & changeBit) == 0) //FALL
  {
    r = true;
    unsigned long current = millis();
    delta = current - prev_fall;
    prev_fall = current;
    if (delta > 50)
    {
      avgTimes[(int)state] = delta;

      unsigned char int_state = (int)state;
      unsigned char new_state = (int_state + 1) > 3 ? 0 : (int_state + 1);
      state = LidarDirection(new_state);
    }
  }

}

void initLidarRotation()
{
  analogWrite(4, 255);

  bool is_next = false;
  while (true)
  {
    if (digitalRead(8) == 0 || digitalRead(9) == 0) //any is hit
    {
      delay(20);
      if (digitalRead(8) == 1 || digitalRead(9) == 1) //only one is hit
      {
        is_next = false;
      }
      else
      {
        if (is_next) break;
        else is_next = true;
      }
      while (digitalRead(8) == 0 || digitalRead(9) == 0) {}
    }
  }
  analogWrite(4, 0);
}

void initLidarEncoder()
{
  cli();
  PCICR |= 1 << PCIE0; //0b00000001; //enable port b (D8 - D13)
  PCMSK0 |= (1 << PCINT0) | (1 << PCINT1); //0b00000011 //enable PCINT0 and PCINT1 (pin 8 and 9)
  sei();
}

void startLidar()
{
  analogWrite(4, 255);
  prev_fall = millis();
  state = LidarDirection::BACK;
}

int getLidarAngle()
{
  unsigned long _current = millis();
  unsigned short _delta = _current - prev_fall;
  float angle = (float)_delta / (float)avgTimes[(int)state] * 90 + (int)state * 90;
  return angle;
}

void setup()
{
  Serial.begin(9600);
  Wire.begin();
  Wire.setClock(400000); // use 400 kHz I2C

  sensor.setTimeout(500);
  if (!sensor.init())
  {
    Serial.println("Failed to detect and initialize sensor!");
    while (1);
  }

  // Use long distance mode and allow up to 50000 us (50 ms) for a measurement.
  // You can change these settings to adjust the performance of the sensor, but
  // the minimum timing budget is 20 ms for short distance mode and 33 ms for
  // medium and long distance modes. See the VL53L1X datasheet for more
  // information on range and timing limits.
  sensor.setDistanceMode(VL53L1X::Short);
  sensor.setMeasurementTimingBudget(16000);

  // Start continuous readings at a rate of one measurement every 50 ms (the
  // inter-measurement period). This period should be at least as long as the
  // timing budget.
  sensor.startContinuous(20);
  

  initLidarRotation();
  initLidarEncoder();
  startLidar();

  delay(1000);
}
 
String LidarDirectionToString(LidarDirection d)
{
  switch (d)
  {
    case LidarDirection::BACK:
      return "BACK";
    case LidarDirection::RIGHT:
      return "RIGHT";
    case LidarDirection::FRONT:
      return "FRONT";
    case LidarDirection::LEFT:
      return "LEFT";
  }
}

void loop()
{
  sensor.read();
  Serial.print(getLidarAngle());
  Serial.print('\t');
  Serial.print(sensor.ranging_data.range_mm);
  Serial.print('\t');
  Serial.print((int)state);
  Serial.print('\t');
  Serial.println(millis() - prev_fall);
}
