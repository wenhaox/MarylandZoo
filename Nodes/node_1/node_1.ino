#include <SoftwareSerial.h>
#include <math.h> // For pow function in extractDigit

#define XBee Serial3

const int myFeederID = 1; // Unique ID for this feeder
long lastSeqNumReceived = 0; // To keep track of the last sequence number received

void setup() {
  Serial.begin(9600);
  XBee.begin(9600); // Initialize XBee communication at 9600 baud
}

void loop() {
  if (XBee.available()) {
    String receivedMsg = XBee.readStringUntil('\n');
    long receivedValue = receivedMsg.toInt();
    long receivedSeqNum = receivedValue / 100000; // Extract the sequence number
    long cmd = receivedValue % 100000; // Extract the command
    
    if (receivedSeqNum <= lastSeqNumReceived) {
      // Duplicate message, ignore it
      Serial.println("Duplicate message received; ignoring.");
    } else {
      lastSeqNumReceived = receivedSeqNum; // Update with the new sequence number
      // Process the command here
      Serial.print("Command processed: ");
      Serial.println(cmd);

      // Send acknowledgment back
      sendCompletionSignal();
    }
  }
}

void sendCompletionSignal() {
  long completionSignal = 2000 + myFeederID; // Prefix 2000 + Feeder ID
  Serial.println(completionSignal);
  XBee.println(completionSignal); // Send completion signal via XBee
  Serial.println("Completion signal sent for this feeder.");
  delay(1000); // Short delay to avoid rapid signal sending
}

int extractDigit(int number, int digitPosition) {
  return (number / int(pow(10, digitPosition))) % 10;
}
