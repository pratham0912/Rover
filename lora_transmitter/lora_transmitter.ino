
// Controller ESP32: Reads PS4 controller and sends joystick data via LoRa

#include <SPI.h>
#include <LoRa.h>
#include <PS4Controller.h>

#define LORA_SS   5
#define LORA_RST  14
#define LORA_DIO0 4

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("LoRa Transmitter");
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(433E6)) {  // Adjust frequency according to your LoRa module
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setTxPower(20);
  LoRa.enableCrc();
  Serial.println("LoRa initialized.");

  PS4.begin();  // Start PS4 controller
}

void loop() {
  if (PS4.isConnected()) {
    int8_t x = PS4.LStickX();
    int8_t y = PS4.LStickY();

    // Send joystick data over LoRa
    LoRa.beginPacket();
    LoRa.write((uint8_t)x);
    LoRa.write((uint8_t)y);
    LoRa.endPacket();

    Serial.printf("Sent -> X:%d  Y:%d\n", x, y);
  }

  delay(20);  // ~50 packets/sec, safe for LoRa
}

