#include <SoftwareSerial.h>

SoftwareSerial XBee(2, 3); // RX, TX on Arduino Uno

void setup() {
  Serial.begin(9600);
  XBee.begin(9600); // Set up XBee communication at 9600 baud
}

void loop() {

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    XBee.println(String(command));

    // Assuming the command format is [command_code][timeout][feeder_id] as discussed
    if (command.length() >= 7) { // Make sure the command is at least 7 characters
      // Extract parts of the command
      String command_code_str = command.substring(0, 3);
      String timeout_str = command.substring(3, 6);
      String feeder_id_str = command.substring(6);

      // Convert to integer
      long command_code = command_code_str.toInt();
      int timeout = timeout_str.toInt(); // Timeout is assumed to be in seconds + xbee com time
      int feeder_id = feeder_id_str.toInt();
      // Calculates the expected response codes
      long desiredResponse = 2000 + feeder_id; // Expected feedback response code
      long timeoutResponse = 3000 + feeder_id; // Expected timeout response code

      // Now wait for acknowledgment
      bool ackReceived = false;
      unsigned long startTime = millis();
      while (!ackReceived && (millis() - startTime) < (timeout * 1000UL + 2000)) { // Convert timeout to milliseconds
        if (XBee.available()) {
          String feedbackStr = XBee.readStringUntil('\n');
          String feedback_code_str = feedbackStr.substring(0, 4);
          long feedback = feedback_code_str.toInt();
          if (feedback == desiredResponse) {
            ackReceived = true;
            Serial.println(String(feedbackStr)); // Print the response
            break; // Exit the loop once acknowledgment is received
          } else if (feedback == timeoutResponse) {
            // Handle timeout response here
            Serial.println(String(feedbackStr));
            break;
          }
        }
      }

      if (!ackReceived) {
        Serial.println("No acknowledgment received within timeout period.");
        //Serial.println(String(timeoutResponse));

      }
    } else {
      Serial.println("Invalid command received."); // Handle invalid command format
    }
  }
}