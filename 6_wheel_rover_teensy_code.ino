#include <Wire.h>
#include "BTS7960.h"

#define SLAVE_ADDR 8
#define PWM_MAX 150
#define DEADZONE 30  // Joystick deadzone

// Left Motors
#define LF_LPWM 2
#define LF_RPWM 3
#define LF_LEN 22
#define LF_REN 23

#define LM_LPWM 10
#define LM_RPWM 11
#define LM_LEN 30
#define LM_REN 31

#define LR_LPWM 4
#define LR_RPWM 5
#define LR_LEN 24
#define LR_REN 25

// Right Motors
#define RF_LPWM 6
#define RF_RPWM 7
#define RF_LEN 26
#define RF_REN 27

#define RM_LPWM 12
#define RM_RPWM 13
#define RM_LEN 32
#define RM_REN 33

#define RR_LPWM 8
#define RR_RPWM 9
#define RR_LEN 28
#define RR_REN 29

// ----- Motor Objects -----
BTS7960 motorLF(LF_LPWM, LF_RPWM, LF_LEN, LF_REN);
BTS7960 motorLM(LM_LPWM, LM_RPWM, LM_LEN, LM_REN);
BTS7960 motorLR(LR_LPWM, LR_RPWM, LR_LEN, LR_REN);

BTS7960 motorRF(RF_LPWM, RF_RPWM, RF_LEN, RF_REN);
BTS7960 motorRM(RM_LPWM, RM_RPWM, RM_LEN, RM_REN);
BTS7960 motorRR(RR_LPWM, RR_RPWM, RR_LEN, RR_REN);

// ----- Joystick Variables -----
uint8_t X = 0;
uint8_t Y = 0;
int x = 0, y = 0;

// ----- Function Prototypes -----
void setupMotors();
void setLeftMotors(int speed);
void setRightMotors(int speed);

void setup() {
  Serial.begin(115200);
  Wire.begin(SLAVE_ADDR);
  Wire.onReceive(receiveEvent);

  setupMotors();

  Serial.println("6-Wheel Rover Ready...");
}

void loop() {
  // Apply deadzone directly
  if (abs(x) < DEADZONE) x = 0;
  if (abs(y) < DEADZONE) y = 0;

  // Calculate side speeds
  int leftSpeed = constrain(map(y + x, -127, 127, -PWM_MAX, PWM_MAX), -PWM_MAX, PWM_MAX);
  int rightSpeed = constrain(map(y - x, -127, 127, -PWM_MAX, PWM_MAX), -PWM_MAX, PWM_MAX);

  // leftSpeed = constrain(leftSpeed, -PWM_MAX, PWM_MAX);
  // rightSpeed = constrain(rightSpeed, -PWM_MAX, PWM_MAX);

  // Set motor speeds
  if(x==0 && y == 0){
    stopMotors();
  }
  else{
  setLeftMotors(leftSpeed);
  setRightMotors(rightSpeed);
  }

  // Debug
  Serial.print("X: "); Serial.print(x);
  Serial.print(" Y: "); Serial.print(y);
  Serial.print(" || Left: "); Serial.print(leftSpeed);
  Serial.print(" Right: "); Serial.println(rightSpeed);

  delay(20);
}

// Functions 
void setupMotors() {
  motorLF.setEnable(true);
  motorLM.setEnable(true);
  motorLR.setEnable(true);
  motorRF.setEnable(true);
  motorRM.setEnable(true);
  motorRR.setEnable(true);
}

void stopMotors() {
  motorLF.stop();
  motorLM.stop();
  motorLR.stop();
  motorRF.stop();
  motorRM.stop();
  motorRR.stop();
}

void setLeftMotors(int speed) {
  motorLF.rotate(speed);
  motorLM.rotate(speed);
  motorLR.rotate(speed);
}

void setRightMotors(int speed) {
  motorRF.rotate(speed);
  motorRM.rotate(speed);
  motorRR.rotate(speed);
}

// I2C receive
void receiveEvent(int byte_received) {
  if (Wire.available() >= 2) {
    X = Wire.read();
    Y = Wire.read();

    x = (X > 127) ? (256 - X) * -1 : X;
    y = (Y > 127) ? (256 - Y) * -1 : Y;

    delay(50);
  }
}
