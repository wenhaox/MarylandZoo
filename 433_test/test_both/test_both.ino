#include <RCSwitch.h>

RCSwitch mySwitch_tx = RCSwitch();
RCSwitch mySwitch_rx = RCSwitch();
void setup() {
  Serial.begin(9600);

  // Receiver setup
  mySwitch_rx.enableReceive(0);  // Receiver on interrupt 0 => that is pin #2

  // Transmitter setup
  mySwitch_tx.enableTransmit(10); // Transmitter is connected to Arduino Pin #10
}

void loop() {
  // Check if something was received
  if (mySwitch_rx.available()) {
    Serial.print("Received ");
    Serial.print(mySwitch_rx.getReceivedValue());
    Serial.print(" / ");
    Serial.print(mySwitch_rx.getReceivedBitlength());
    Serial.print("bit ");
    Serial.print("Protocol: ");
    Serial.println(mySwitch_rx.getReceivedProtocol());
    mySwitch_rx.resetAvailable();
  }

  // Transmit a signal
  mySwitch_tx.send(1, 24); // Example signal, adjust as needed
  Serial.println("Sent ");
  delay(1000); // Delay to allow for reception before the next transmission

  // Note: You might need to adjust the delay or implement a more sophisticated
  // mechanism to switch between sending and receiving modes based on your specific needs.
}
