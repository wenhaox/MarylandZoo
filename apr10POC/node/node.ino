#include <DFRobotDFPlayerMini.h>

const int actuator_pos_pin = 6;
const int actuator_neg_pin = 5;
const int ultrasonic_relay_pin = 8;

int success_distance = 200;
unsigned long timeout = 180000;
unsigned long start_timeout; 
unsigned long completion_time;
// Initializes variables used in detection function
unsigned char data[4] = {};
float distance;

int mp3volume = 20;          // volume of audio played from speaker. Must be between 0-30 (Default is 20)
int audio_loop = 10;  // Number of times audio sound is played while node is active (default is 10 times)
int sound = 1;  // Determines which audio file is played from SD card -- corresponds to order of library on sd card (default is first file; currently gopher scream)
int audio_timer;
int false_pos_counter;

bool success;  // Bool used to determine success or failure in node

#define mp3_serial Serial1
#define ultrasonic_serial Serial2
#define xbee_serial Serial3

const int myFeederID = 1; // Unique ID for this feeder

DFRobotDFPlayerMini myDFPlayer;

void setup() {
  Serial.begin(9600);  // Creates serial
  mp3_serial.begin(9600);
  ultrasonic_serial.begin(9600);
  xbee_serial.begin(9600);

  pinMode(ultrasonic_relay_pin, OUTPUT);
  digitalWrite(ultrasonic_relay_pin, LOW);

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
  myDFPlayer.volume(mp3volume);
  
  // Initialize linear actuator
  pinMode(actuator_pos_pin, OUTPUT);
  pinMode(actuator_neg_pin, OUTPUT);
  digitalWrite(actuator_pos_pin, LOW);
  digitalWrite(actuator_neg_pin, LOW);
  delay(1000);

  // Raise linear actuator if not raised already
  digitalWrite(actuator_pos_pin, HIGH);
  delay(2000);
  digitalWrite(actuator_pos_pin, LOW);
}

void loop() {
  // Initialize loop variables for first iteration (Should only repeat once per node activation)
  false_pos_counter = 0;
  success = false;
  completion_time = timeout / 1000;
  audio_timer = (timeout/1000) / audio_loop;
  digitalWrite(ultrasonic_relay_pin, HIGH);
  start_timeout = millis();
  PlayAudio(sound);

  if (xbee_serial.available()) {
    Serial.println("Done");
    String receivedMessage = xbee_serial.readStringUntil('\n');
    long receivedValue = receivedMessage.toInt();
    int command = receivedValue / 10; // Extract command prefix
    int feederID = extractDigit(receivedValue, 0); // Extract feeder ID

    if (feederID == myFeederID) {
      if (command == 100) { // Activation command received
        Serial.println("Activation command received for this feeder.");
        // Perform the feeder's task here
        myDFPlayer.play(2);
        delay(2000);
        // After completing the task, send a completion signal
        sendCompletionSignal();
      }
      if (command == 101) { // Ball node
        Serial.println("Ball activation command received for this feeder.");
        // Perform the feeder's task here
        myDFPlayer.play(2);
        delay(2000);
        BallRelease();
        // After completing the task, send a completion signal
        sendCompletionSignal();
      }
      if (command == 201) { // Autonomous node
        Serial.println("Autonomous command received for this feeder.");
        // Active node detection loop; Remains true while nothing is within detection radius and node has not reached timeout limit to be considered failure
        while (false_pos_counter < 15 && (millis() - start_timeout < timeout)) {
          if ((((millis() - start_timeout)/1000) % audio_timer) == 0){
              PlayAudio(2);
            }
          distance = Detect();
          if(distance < success_distance){
            false_pos_counter++; // Increment false positives by 1
          } else {
            false_pos_counter = 0;
          }
          Serial.print("Distance: ");
          Serial.println(distance / 10);
        }
        // Determines if bobcat was successful; above while loop breaks if bobcat is detected or node times out.
        // If statement verifies node did not timeout (which means bobcat was successful)
        if (millis() - start_timeout < timeout) {
          success = true;
          completion_time = (millis() - start_timeout); // 1000;  // Measures time to complete (in seconds) (DELETE/CHANGE IF IMPLEMENT RTC MODULE)
        }
        Serial.print("Pos Counter: ");
        Serial.print(false_pos_counter);
        Serial.print(" Distance: ");
        Serial.print(distance / 10);
        Serial.print(" Timeout Time: ");
        Serial.print(timeout);
        Serial.print(" Completion Time: ");
        Serial.println(completion_time);
        delay(1000);
        // NEED TO INCLUDE LOGIC FOR XBEE COMS AND HANDLING OF FINAL NODE VS NOT FINAL NODE
        if (success) {
          BallRelease();
        }
        digitalWrite(ultrasonic_relay_pin, LOW);
        sendCompletionSignal();
      }
    }
  }
}

void sendCompletionSignal() {
  long completionSignal = 2000 + myFeederID; // Prefix 200 + Feeder ID
  String message = String(completionSignal) + "\n"; // Ensure to end with newline for readStringUntil()
  Serial.println(completionSignal);
  xbee_serial.print(message); // Send completion signal over RF
  Serial.println("Completion signal sent for this feeder.");
  delay(1000); // Short delay to avoid rapid signal sending
}

int extractDigit(long number, int digitPosition) {
  return (number / long(pow(10, digitPosition))) % 10;
}

// Function BallRelease: Lowers linear actuator to release the ball and then raises it back up to original position ready to be loaded again.
void BallRelease() {
  digitalWrite(actuator_neg_pin, HIGH);
  digitalWrite(actuator_pos_pin, LOW);
  delay(3000);
  digitalWrite(actuator_neg_pin, LOW);


  // Resets actuator to fully extended position
  digitalWrite(actuator_pos_pin, HIGH);
  delay(4000);
  digitalWrite(actuator_pos_pin, LOW);
}


// Function PlayAudio: Plays specified audio file at given volume defined
void PlayAudio(int sound) {
  myDFPlayer.play(sound);
}


// Function Detect: Returns distance away an object is from node in mm; ultrasonic sensor requires ~1/10s delay between each reading for better accuracy
// Code based off sample code from DFRobot website (just google waterproof ultrasonic sensor)
float Detect() {
  do {
    for (int i = 0; i < 4; i++) {
      data[i] = ultrasonic_serial.read();
    }
  } while (ultrasonic_serial.read() == 0xff);

  ultrasonic_serial.flush();

  if (data[0] == 0xff) {
    int sum;
    sum = (data[0] + data[1] + data[2]) & 0x00FF;
    if (sum == data[3]) {
      distance = (data[1] << 8) + data[2];
      if (distance > 30)  // 30 mm is min detect distance
      {
        return distance;
        delay(100);
      } else  // If the object is closer than the minimum detect distance, wait 1/10 s and take another reading
      {
        delay(100);
        return Detect();
      }
    } else {
      delay(100);
      return Detect();  // If error in reading data, wait 1/10s and take another reading
    }
  }
}


