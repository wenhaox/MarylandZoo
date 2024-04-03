#include <NeoSWSerial.h>

NeoSWSerial XBee(2, 3); 

const int button1Pin = 7; 
bool lastButton1State = HIGH; 
const int button2Pin = 6; 
bool lastButton2State = HIGH; 

void setup() {
  XBee.begin(9600);
  Serial.begin(9600);

  pinMode(button1Pin, INPUT_PULLUP);
  pinMode(button2Pin, INPUT_PULLUP);
}

void loop() {
  bool currentButton1State = digitalRead(button1Pin);
  bool currentButton2State = digitalRead(button2Pin);

  if (lastButton1State == HIGH && currentButton1State == LOW) {
    XBee.println("1001");
    Serial.println("Sent 1001");
  }
  if (lastButton2State == HIGH && currentButton2State == LOW) {
    XBee.println("1011");
    Serial.println("Sent 1011");
  }

  lastButton1State = currentButton1State;
  lastButton2State = currentButton2State;
  delay(50);
}
