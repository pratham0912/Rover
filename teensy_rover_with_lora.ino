// Teensy

#include <Wire.h>
#include "BTS7960.h"

#define SLAVE_ADDR 8
#define PWM_MAX 150
#define DEADZONE 30

// Left motors
#define LF_LPWM 11
#define LF_RPWM 10
#define LR_LPWM 8
#define LR_RPWM 9

// Right motors
#define RF_LPWM 6
#define RF_RPWM 7
#define RR_LPWM 2
#define RR_RPWM 3

BTS7960 motorLF(LF_LPWM, LF_RPWM);
BTS7960 motorLR(LR_LPWM, LR_RPWM);
BTS7960 motorRF(RF_LPWM, RF_RPWM);
BTS7960 motorRR(RR_LPWM, RR_RPWM);

int8_t x = 0, y = 0;
int leftSpeed = 0, rightSpeed = 0;

uint8_t byteX = 0; // raw byte from I2C
uint8_t byteY = 0; // raw byte from I2C

void setup() {
  Serial.begin(115200);
  Wire.begin();  // Master

  // Enable motors
  motorLF.setEnable(true);
  motorLR.setEnable(true);
  motorRF.setEnable(true);
  motorRR.setEnable(true);

  Serial.println("Mega/Teensy Master Ready");
}

void loop() {
  // Poll ESP32 for joystick
  Wire.requestFrom(SLAVE_ADDR, 2);
  if (Wire.available() >= 2) {
    byteX = Wire.read();
    byteY = Wire.read();

    // Convert to signed
    x = (byteX > 127) ? byteX - 256 : byteX;
    y = (byteY > 127) ? byteY - 256 : byteY;
  }

  // Apply deadzone
  if (abs(x) < DEADZONE) x = 0;
  if (abs(y) < DEADZONE) y = 0;

  // Tank drive computation
  leftSpeed  = map(y + x, -127, 127, -PWM_MAX, PWM_MAX);
  rightSpeed = map(y - x, -127, 127, -PWM_MAX, PWM_MAX);

  leftSpeed  = constrain(leftSpeed, -PWM_MAX, PWM_MAX);
  rightSpeed = constrain(rightSpeed, -PWM_MAX, PWM_MAX);

  // Drive motors
  if (x == 0 && y == 0) {
    motorLF.stop();
    motorLR.stop();
    motorRF.stop();
    motorRR.stop();
  } else {
    motorLF.rotate(leftSpeed);
    motorLR.rotate(leftSpeed);
    motorRF.rotate(rightSpeed);
    motorRR.rotate(rightSpeed);
  }

  // Debug print
  Serial.println((String)"Joystick X:" + x + " Y:" + y + " L:" + leftSpeed + " R:" + rightSpeed);

  delay(20);
}
