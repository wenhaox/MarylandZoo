#include <RCSwitch.h>

RCSwitch mySwitch_tx = RCSwitch();
RCSwitch mySwitch_rx = RCSwitch();

const int transmitterPin = 10; // Pin connected to the RF transmitter
const int receiverInterrupt = 0; // Interrupt connected to the RF receiver, pin 2 on most Arduinos
const int myFeederID = 1; // Unique ID for this feeder

void setup() {
  Serial.begin(9600);
  mySwitch_tx.enableTransmit(transmitterPin);
  mySwitch_rx.enableReceive(receiverInterrupt); // Receiver on interrupt 0 => that is pin #2
}

void loop() {
  // Check if a command is received via RF
  if (mySwitch_rx.available()) {
    long receivedValue = mySwitch_rx.getReceivedValue();
    //Serial.println(receivedValue);
    int command = receivedValue / 10; // Extract command prefix
    int feederID = extractDigit(receivedValue, 0); // Extract feeder ID
    //Serial.println(command);
    //Serial.println(feederID);
    if (feederID == myFeederID) {
      if (command == 100) { // Activation command received
        Serial.println("Activation command received for this feeder.");
        // Perform the feeder's task here
    
        // After completing the task, send a completion signal
        sendCompletionSignal();
      }
      if (command == 101) { //ball node
        Serial.println("Ball activation command received for this feeder.");
        // Perform the feeder's task here
        //Serial.println(command);
        // After completing the task, send a completion signal
        sendCompletionSignal();
      }
    }
    mySwitch_rx.resetAvailable();
  }
}

void sendCompletionSignal() {
  long completionSignal = 2000 + myFeederID; // Prefix 200 + Feeder ID
  Serial.println(completionSignal);
  mySwitch_tx.send(completionSignal, 24); // Send completion signal
  Serial.println("Completion signal sent for this feeder.");
  delay(1000); // Short delay to avoid rapid signal sending
}

int extractDigit(int number, int digitPosition) {
  return (number / int(pow(10, digitPosition))) % 10;
}
