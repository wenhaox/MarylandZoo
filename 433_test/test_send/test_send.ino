#include <RCSwitch.h>

RCSwitch mySwitch = RCSwitch();

void setup() {
  Serial.begin(9600);
  // Transmitter is connected to Arduino Pin #10  
  mySwitch.enableTransmit(10);
}

void loop() {
    mySwitch.send(1, 24); // Example signal, adjust as needed
    delay(1000); // Delay between signals if necessary
}