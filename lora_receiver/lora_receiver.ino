// Rover ESP32: Receives joystick data via LoRa and forwards it to Mega via I²C

#include <SPI.h>
#include <LoRa.h>
#include <Wire.h>

#define LORA_SS   5
#define LORA_RST  14
#define LORA_DIO0 4 
#define SLAVE_ADDR 8  // I2C slave address for Mega

int8_t joyX = 0;
int8_t joyY = 0;

void setup() {
  Serial.begin(115200);

  // I2C setup
  Wire.begin(SLAVE_ADDR);
  Wire.onRequest(sendData); 

  // LoRa setup
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(433E6)) {  // Must match transmitter frequency
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.enableCrc();
  Serial.println("LoRa + I2C Bridge Ready");
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize >= 2) {
    joyX = (int8_t)LoRa.read();
    joyY = (int8_t)LoRa.read();

    Serial.print("LoRa Received -> X: ");
    Serial.print(joyX);
    Serial.print("  Y: ");
    Serial.println(joyY);
  }
   Wire.write((uint8_t)joyX);
  Wire.write((uint8_t)joyY);

}

// Sends joystick data to Mega when requested via I2C
void sendData() {
  Wire.write((uint8_t)joyX);
  Wire.write((uint8_t)joyY);
}
