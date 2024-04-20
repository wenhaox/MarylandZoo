#include <SoftwareSerial.h>

SoftwareSerial XBee(2, 3); // RX, TX on Arduino Uno

void setup() {
  Serial.begin(9600);
  XBee.begin(9600); // Set up XBee communication at 9600 baud
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    long cmd = command.toInt();
    Serial.println(cmd);
    long desiredResponse = 2000 + (cmd % 10); // Calculates the expected response

    // Send the command once
    XBee.println(cmd);

    // Now wait for acknowledgment
    bool ackReceived = false;
    unsigned long startTime = millis();
    while (!ackReceived && (millis() - startTime) < 30000) { // 10-second timeout
      if (XBee.available()) {
        String feedbackStr = XBee.readStringUntil('\n');
        long feedback = feedbackStr.toInt();
        if (feedback == desiredResponse) {
          ackReceived = true;
          Serial.println(String(desiredResponse)); // Print the response
          break; // Exit the loop once acknowledgment is received
        }
      }
    }

    if (!ackReceived) {
      Serial.println("No acknowledgment received."); // Inform if no acknowledgment received
    }
  }
}
