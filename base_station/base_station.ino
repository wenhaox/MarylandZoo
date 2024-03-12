#include <RCSwitch.h>

RCSwitch mySwitch_tx = RCSwitch();
RCSwitch mySwitch_rx = RCSwitch();
unsigned long lastSeqNum = 0; // Sequence number for messages

void setup() {
  Serial.begin(9600);
  mySwitch_tx.enableTransmit(10); // Transmitter on Pin 10
  mySwitch_rx.enableReceive(0); // Receiver on interrupt 0 => Pin 2
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    long cmd = command.toInt();
    lastSeqNum++; // Increment sequence number for each new command
    long fullCmd = lastSeqNum * 100000 + cmd; // Combine sequence number and command

    bool ackReceived = false;
    unsigned long startTime = millis();
    while (!ackReceived && (millis() - startTime) < 10000) { // 10-second timeout
      mySwitch_tx.send(fullCmd, 24); // Send combined sequence number and command as RF signal
      delay(500); // Wait for a bit before checking for acknowledgment
      if (mySwitch_rx.available()) {
        long feedback = mySwitch_rx.getReceivedValue();
        if (feedback == (fullCmd + 1000)) { // Assuming ACK is command + 1000
          ackReceived = true;
          Serial.println("ACK received");
        }
        mySwitch_rx.resetAvailable();
      }
    }
    if (!ackReceived) {
      Serial.println("ACK not received, check receiver.");
    }
  }
}