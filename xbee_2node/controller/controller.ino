#include <SoftwareSerial.h>

SoftwareSerial XBee(2, 3); 

const int buttonPin = 7; 
bool lastButtonState = HIGH; 

void setup() {
  XBee.begin(9600);
  Serial.begin(9600);

  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  if (Serial.available()) { 
    XBee.write(Serial.read());
  }

  if (XBee.available()) {
    Serial.write(XBee.read());
  }

  bool currentButtonState = digitalRead(buttonPin);
  if (lastButtonState == HIGH && currentButtonState == LOW) {
    XBee.println("1001");
    Serial.println("Sent 1001");
  }
  lastButtonState = currentButtonState;

  delay(50);
}
