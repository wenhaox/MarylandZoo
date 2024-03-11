#define ionizer_pin 6

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(ionizer_pin, OUTPUT);
  digitalWrite(ionizer_pin, LOW);
  

}

void loop() {
  digitalWrite(ionizer_pin, HIGH);
  delay(5000); //How long it diffuses scent for
  digitalWrite(ionizer_pin, LOW);
  delay(5000);
  Serial.println("2");

}
