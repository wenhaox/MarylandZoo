#include <NeoSWSerial.h>
#include <DFRobotDFPlayerMini.h>

// Pins for SoftwareSerial
const int rxPin = 2; // Connect to the TX pin of the RF module
const int txPin = 3; // Connect to the RX pin of the RF module
const int mp3TX_pin = 12; 
const int mp3RX_pin = 11;
const int actuator_pos_pin = 6;
const int actuator_neg_pin = 5;

#define mp3_serial Serial1
#define ultrasonic_serial Serial2
#define xbee_serial Serial3

const int myFeederID = 1; // Unique ID for this feeder

void setup() {
  Serial.begin(9600);
  XBee.begin(9600); // Initialize SoftwareSerial port
  mp3_serial.begin(9600);

   //Initialize mp3 module
  if (!myDFPlayer.begin(mp3_serial)) {  //Use softwareSerial to communicate with mp3.
    Serial.println(F("Unable to begin:"));
    Serial.println(F("1.Please recheck the connection!"));
    Serial.println(F("2.Please insert the SD card!"));
    while (true) {
      delay(0);  // Code to compatible with ESP8266 watch dog.

    }
  }
  myDFPlayer.begin(mp3_serial);
  myDFPlayer.volume(20);

}

void loop() {
  // Check if a command is received via RF
  if (XBee.available()) {
      Serial.println("Done");
    String receivedMessage = XBee.readStringUntil('\n');
    long receivedValue = receivedMessage.toInt();
    int command = receivedValue / 10; // Extract command prefix
    int feederID = extractDigit(receivedValue, 0); // Extract feeder ID

    if (feederID == myFeederID) {
      if (command == 100) { // Activation command received
        Serial.println("Activation command received for this feeder.");
        // Perform the feeder's task here
        //myDFPlayer.play(1);
        //delay(2000);
        // After completing the task, send a completion signal
        sendCompletionSignal();
      }
      if (command == 101) { // Ball node
        Serial.println("Ball activation command received for this feeder.");
        // Perform the feeder's task here
        //myDFPlayer.play(1);
        //delay(1000);
        BallRelease();
        // After completing the task, send a completion signal
        sendCompletionSignal();
      }
      if (command == 201) { // Ball node
        Serial.println("Autonomous command received for this feeder.");
        // Perform the feeder's task here
        //myDFPlayer.play(1);
        //delay(1000);
        BallRelease();
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

void BallRelease() {
  digitalWrite(actuator_neg_pin, HIGH);
  digitalWrite(actuator_pos_pin, LOW);
  delay(3000);
  digitalWrite(actuator_neg_pin, LOW);


  //Resets actuator to fully extened position
  //digitalWrite(actuator_pos_pin, HIGH);
  //delay(4000);
  //digitalWrite(actuator_pos_pin, LOW);
}

