#include <RCSwitch.h>
#include <math.h> // For pow function in extractDigit

RCSwitch mySwitch_tx = RCSwitch();
RCSwitch mySwitch_rx = RCSwitch();

const int transmitterPin = 10; // Pin connected to the RF transmitter
const int receiverInterrupt = 0; // Interrupt connected to the RF receiver, pin 3 on most Arduinos
const int myFeederID = 1; // Unique ID for this feeder
long lastSeqNumReceived = 0; // To keep track of the last sequence number received

void setup() {
  Serial.begin(9600);
  mySwitch_tx.enableTransmit(transmitterPin);
  mySwitch_rx.enableReceive(receiverInterrupt); // Receiver on interrupt 0 => that is pin #2
}

void loop() {
  if (mySwitch_rx.available()) {
    Serial.println("Inside");
    long receivedValue = mySwitch_rx.getReceivedValue();
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