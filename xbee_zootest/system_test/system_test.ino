/*
JHU MultiD Zoo Team "Node Code"
Will Leger, Raphael Stadler, Peter Xu, Jonathan Liu
Code is designed for Node #1
Sample RF signal breakdown: 1ag
1=node number
a=not final node
g=sound designation
*/


#include <SoftwareSerial.h>
#include <DFRobotDFPlayerMini.h>




#define mp3_serial Serial1
#define ultrasonic_serial Serial2
#define xbee_serial Serial3


const int actuator_pos_pin = 6;
const int actuator_neg_pin = 5;


const int ultrasonic_relay_pin = 8;


int mp3volume = 20;          // volume of audio played from speaker. Must be between 0-30 (Default is 20)
int success_distance = 200;  // Distance (in mm) from the ultrasonic sensor that is considered a "success" by the bobcat. Must be greater than 30 mm (Default is 20 cm)


// int detect_time = 0;    // Times how long an object has been detected using the detect function. Implemented to prevent false positives


unsigned long start_timeout;  // Initialized at the start of each node activation -- used as reference for starting time of node


unsigned long timeout = 180000;  // Timeout for each node in milliseconds (default is 3 minutes (180000))


unsigned long completion_time;  // Time it takes for bobcat to successfully complete node


int audio_loop = 10;  // Number of times audio sound is played while node is active (default is 10 times)


int sound = 1;  // Determines which audio file is played from SD card -- corresponds to order of library on sd card (default is first file; currently gopher scream)


bool success;  // Bool used to determine success or failure in node


int audio_timer;


int false_pos_counter;


DFRobotDFPlayerMini myDFPlayer;




// Initializes variables used in detection function
unsigned char data[4] = {};
float distance;


void setup() {
  Serial.begin(9600);  // Creates serial
  mp3_serial.begin(9600);
  ultrasonic_serial.begin(9600);


  pinMode(ultrasonic_relay_pin, OUTPUT);
  digitalWrite(ultrasonic_relay_pin, LOW);


  // Configure audio player with selected audio file and volume
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
  // Handle XBee Coms


  // Initialize loop variables for first iteration (Should only repeat once per node activation)
  false_pos_counter = 0;
  success = false;
  completion_time = timeout / 1000;
  audio_timer = (timeout/1000) / audio_loop;
  digitalWrite(ultrasonic_relay_pin, HIGH);
  start_timeout = millis();
  // distance = Detect();
  PlayAudio(sound);


  // Active node detection loop; Remains true while nothing is within detection radius and node has not reached timeout limit to be considered failure
  while (false_pos_counter < 15 && (millis() - start_timeout < timeout)) {
    if ((((millis() - start_timeout)/1000) % audio_timer) == 0){
        PlayAudio(sound);
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
  exit(0);
}




/*
Helper Functions
*/


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


// void SendBack() {
// }

