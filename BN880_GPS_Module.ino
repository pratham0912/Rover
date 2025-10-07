#include <TinyGPS++.h>

TinyGPSPlus gps;

// Use Serial1 for BN-880 on Arduino Mega
#define gpsSerial Serial1  

void setup() {
  Serial.begin(9600);         
  gpsSerial.begin(9600);       // BN-880 default baud rate

  Serial.println("BN-880 GPS Module Test - Arduino Mega");
}

void loop() {
  // Continuously check for incoming GPS data
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());

    // When new location data is available
    if (gps.location.isUpdated()) {
      Serial.print("Latitude: ");
      Serial.print(gps.location.lat(), 6);
      Serial.print(", Longitude: ");
      Serial.println(gps.location.lng(), 6);
    }

    // Optional info — uncomment if you want to debug
    /*
    if (gps.altitude.isUpdated()) {
      Serial.print("Altitude: ");
      Serial.print(gps.altitude.meters());
      Serial.println(" m");
    }

    if (gps.satellites.isUpdated()) {
      Serial.print("Satellites: ");
      Serial.println(gps.satellites.value());
    }

    if (gps.speed.isUpdated()) {
      Serial.print("Speed: ");
      Serial.print(gps.speed.kmph());
      Serial.println(" km/h");
    }
    */
  }
}
