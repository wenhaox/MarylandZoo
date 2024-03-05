#include <RCSwitch.h>

RCSwitch mySwitch_tx = RCSwitch();
RCSwitch mySwitch_rx = RCSwitch();

void setup() {
  Serial.begin(9600);
  // Transmitter is connected to Arduino Pin #10
  // Receiver to interrupt 0 => pin #2 for feedback
  mySwitch_tx.enableTransmit(10);
  mySwitch_rx.enableReceive(0);  // Assuming pin #2 is for the receiver
}

void loop() {
  // Send commands to feeders
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    long cmd = command.toInt();
    mySwitch_tx.send(cmd, 24); // Send command as RF signal
  }
  
  // Listen for feedback from feeders
  if (mySwitch_rx.available()) {
    long feedback = mySwitch_rx.getReceivedValue();
    Serial.println(String(feedback));  // Send feedback to dashboard
    mySwitch_rx.resetAvailable();
  }
}