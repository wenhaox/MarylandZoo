#include <NeoSWSerial.h>

// Pins for SoftwareSerial
const int rxPin = 2; // Connect to the TX pin of the RF module
const int txPin = 3; // Connect to the RX pin of the RF module

NeoSWSerial XBee(rxPin, txPin); // RX, TX

const int myFeederID = 1; // Unique ID for this feeder

void setup() {
  Serial.begin(9600);
  XBee.begin(9600); // Initialize SoftwareSerial port
}

void loop() {
  // Check if a command is received via RF
  if (XBee.available()) {
    String receivedMessage = XBee.readStringUntil('\n');
    long receivedValue = receivedMessage.toInt();
    int command = receivedValue / 10; // Extract command prefix
    int feederID = extractDigit(receivedValue, 0); // Extract feeder ID

    if (feederID == myFeederID) {
      if (command == 100) { // Activation command received
        Serial.println("Activation command received for this feeder.");
        // Perform the feeder's task here
    
        // After completing the task, send a completion signal
        sendCompletionSignal();
      }
      if (command == 101) { // Ball node
        Serial.println("Ball activation command received for this feeder.");
        // Perform the feeder's task here

        // After completing the task, send a completion signal
        sendCompletionSignal();
      }
    }
  }
}

void sendCompletionSignal() {
  long completionSignal = 2000 + myFeederID; // Prefix 200 + Feeder ID
  String message = String(completionSignal) + "\n"; // Ensure to end with newline for readStringUntil()
  Serial.println(completionSignal);
  XBee.print(message); // Send completion signal over RF
  Serial.println("Completion signal sent for this feeder.");
  delay(1000); // Short delay to avoid rapid signal sending
}

int extractDigit(long number, int digitPosition) {
  return (number / long(pow(10, digitPosition))) % 10;
}
