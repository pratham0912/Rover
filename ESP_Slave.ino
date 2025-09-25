#include <PS4Controller.h>
#include <Wire.h>

#define SLAVE_ADDR 8  // ESP32 I2C address

int8_t joyX = 0;
int8_t joyY = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin(SLAVE_ADDR);        
  Wire.onRequest(sendData);       // Send joystick data when Master requests

  PS4.begin();
  Serial.println("Waiting for PS4 controller...");
  delay(2000);
}

void loop() {
  if (PS4.isConnected()) {
    joyX = PS4.LStickX();  
    joyY = PS4.LStickY();
  }
  delay(10);  
}


void sendData() {
  Wire.write((uint8_t)joyX);  
  Wire.write((uint8_t)joyY);  
  Serial.print("X : ");
  Serial.print(joyX);
  Serial.print("     ||     Y : ");
  Serial.println(joyY);
}
