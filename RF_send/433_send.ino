#include <RCSwitch.h>

RCSwitch mySwitch = RCSwitch();

void setup() {
  Serial.begin(9600);
  // Transmitter is connected to Arduino Pin #10  
  mySwitch.enableTransmit(10);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read the command until newline
    if(command == "SEND_RF") {
      // Trigger RF signal transmission
      mySwitch.send(1, 24); // Example signal, adjust as needed
      delay(1000); // Delay between signals if necessary
    }
  }
}