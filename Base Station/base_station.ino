#include <SoftwareSerial.h>

SoftwareSerial XBee(2, 3); // RX, TX on Arduino Uno
unsigned long lastSeqNum = 0; // Sequence number for messages

void setup() {
  Serial.begin(9600);
  XBee.begin(9600); // Set up XBee communication at 9600 baud
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    long cmd = command.toInt();
    lastSeqNum++; // Increment sequence number for each new command
    long fullCmd = lastSeqNum * 100000 + cmd; // Combine sequence number and command
    long desiredResponse = 2000 + (cmd % 10);

    bool ackReceived = false;
    unsigned long startTime = millis();
    while (!ackReceived && (millis() - startTime) < 10000) { // 10-second timeout
      XBee.println(fullCmd); // Send combined sequence number and command via XBee
      delay(500); // Wait for a bit before checking for acknowledgment
      while (XBee.available()) {
        String feedbackStr = XBee.readStringUntil('\n');
        long feedback = feedbackStr.toInt();
        if (feedback == desiredResponse) {
          ackReceived = true;
          Serial.println(String(desiredResponse));
        }
      }
    }
  }
}
