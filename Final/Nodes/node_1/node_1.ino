#include <SoftwareSerial.h>
#include <math.h> // For pow function in extractDigit
#include <DFRobotDFPlayerMini.h>

const int actuator_pos_pin = 6;
const int actuator_neg_pin = 5;
const int ultrasonic_relay_pin = 8;

// 
int success_distance = 200;
unsigned long start_time; 

// Initializes variables used in detection function
unsigned char data[4] = {};
float distance;

int mp3volume = 20;   // volume of audio played from speaker. Must be between 0-30 (Default is 20)
int audio_loop = 1;  // Number of times audio sound is played while node is active (default is 10 times)
int audio_file = 1;        // Determines which audio file is played from SD card -- corresponds to order of library on sd card (default is first file; currently gopher scream)
int audio_timer;
int false_pos_counter;
long completion_time;

bool success;  // Bool used to determine success or failure in node

#define mp3_serial Serial1
#define ultrasonic_serial Serial2
#define XBee Serial3

DFRobotDFPlayerMini myDFPlayer;
const int myFeederID = 2; // Unique ID for this feeder
long lastSeqNumReceived = 0; // To keep track of the last sequence number received

void setup() {
  Serial.begin(9600);
  mp3_serial.begin(9600);
  ultrasonic_serial.begin(9600);
  XBee.begin(9600); // Initialize XBee communication at 9600 baud

  pinMode(ultrasonic_relay_pin, OUTPUT);
  digitalWrite(ultrasonic_relay_pin, LOW);

  // Initialize mp3 module
  if (!myDFPlayer.begin(mp3_serial)) {  // Use softwareSerial to communicate with mp3.
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

  digitalWrite(ultrasonic_relay_pin, HIGH);
  delay(50);
  digitalWrite(ultrasonic_relay_pin, LOW);
  start_time = millis();
  PlayAudio(audio_file);

  if (XBee.available()) {
    String receivedMsg = XBee.readStringUntil('\n');
    Serial.println(receivedMsg);

    // Assuming command format is [command_code][timeout][feeder_id][audio_file]
    if (receivedMsg.length() >= 8) {
      long cmd = receivedMsg.substring(0, 3).toInt();
      long receivedTimeout = receivedMsg.substring(3, 6).toInt() * 1000; // convert to milliseconds
      int feederID = receivedMsg.substring(7).toInt();
      audio_file = receivedMsg.substring(6, 7).toInt();
      Serial.println(receivedMsg);
      audio_timer = (receivedTimeout / 1000) / audio_loop;

      if (feederID == myFeederID) {
        if (cmd == 101) { // Feed
          Serial.println("Autonomous command received for this feeder.");
          digitalWrite(ultrasonic_relay_pin, HIGH);
          // Active node detection loop; Remains true while nothing is within detection radius and node has not reached timeout limit to be considered failure
          while ((millis() - start_time < receivedTimeout)) {
            if ((((millis() - start_time) / 1000) % audio_timer) == 0) {
              PlayAudio(audio_file);
            }
            distance = Detect();
            if (distance < success_distance) {
              false_pos_counter++; // Increment false positives by 1
              if (false_pos_counter >= 15) { // If the object has been consistently detected
                success = true; // Set success to true
                completion_time = millis() - start_time; // Capture the time of success
                break; // Break out of the loop
              }
            } else {
              false_pos_counter = 0;
            }
            Serial.print("Distance: ");
            Serial.println(distance / 10);
          }
          // Determines if bobcat was successful; above while loop breaks if bobcat is detected or node times out.
          // If statement verifies that the node did not timeout (which means bobcat was successful)
          myDFPlayer.pause();
          Serial.print("Pos Counter: ");
          Serial.print(false_pos_counter);
          Serial.print(" Distance: ");
          Serial.println(distance / 10);
          delay(1000);

          // NEED TO INCLUDE LOGIC FOR XBEE COMS AND HANDLING OF FINAL NODE VS NOT FINAL NODE
          if (success) {
            sendCompletionSignal(completion_time);
            BallRelease();
            // other success logic
          } else {
            sendTimeoutSignal();
          }
          digitalWrite(ultrasonic_relay_pin, LOW);
        }
        if (cmd == 100) { // NoFeed
          Serial.println("Autonomous command received for this feeder.");
          digitalWrite(ultrasonic_relay_pin, HIGH);
          // Active node detection loop; Remains true while nothing is within detection radius and node has not reached timeout limit to be considered failure
          while ((millis() - start_time < receivedTimeout)) {
            if ((((millis() - start_time) / 1000) % audio_timer) == 0) {
              PlayAudio(audio_file);
            }
            distance = Detect();
            if (distance < success_distance) {
              false_pos_counter++; // Increment false positives by 1
              if (false_pos_counter >= 15) { // If the object has been consistently detected
                success = true; // Set success to true
                completion_time = millis() - start_time; // Capture the time of success
                break; // Break out of the loop
              }
            } else {
              false_pos_counter = 0;
            }
            Serial.print("Distance: ");
            Serial.println(distance / 10);
          }
          // Determines if bobcat was successful; above while loop breaks if bobcat is detected or node times out.
          // If statement verifies that the node did not timeout (which means bobcat was successful)
          myDFPlayer.pause();
          Serial.print("Pos Counter: ");
          Serial.print(false_pos_counter);
          Serial.print(" Distance: ");
          Serial.println(distance / 10);
          delay(1000);

          // NEED TO INCLUDE LOGIC FOR XBEE COMS AND HANDLING OF FINAL NODE VS NOT FINAL NODE
          if (success) {
            sendCompletionSignal(completion_time);
            
            // other success logic
          } else {
            sendTimeoutSignal();
          }
          digitalWrite(ultrasonic_relay_pin, LOW);
        }
        Serial.print("Command processed: ");
        Serial.println(cmd);
      } // Close feederID if
    } // Close receivedMsg length if
  } // Close XBee.available if
} // Close loop function

void sendCompletionSignal(unsigned long completionTime) {
  completionTime = completionTime/1000;
  char buffer[20]; // Buffer size assumes that the resulting string is not too long
  // Format the completion signal with feeder ID and padded completion time
  sprintf(buffer, "%d%03lu", 2000 + myFeederID, completionTime);

  String completionSignal = String(buffer);
  Serial.println(completionSignal);
  XBee.println(completionSignal); // Send completion signal via XBee
  Serial.println("asdasd");
  Serial.println("Completion signal with padded time sent for this feeder.");
}



void sendTimeoutSignal() {
  String timeoutSignal = String(3000 + myFeederID);
  XBee.println(timeoutSignal);
  Serial.println("Timeout signal sent: " + timeoutSignal);
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
void PlayAudio(int audio_file) {
  myDFPlayer.play(audio_file);
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
