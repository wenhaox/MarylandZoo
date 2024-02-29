#include <ArduinoJson.h>
#include <SPI.h>
#include <SD.h>

//JSON file is named "feed_time.json" and stored on an SD card
const char *filename = "/config.json";

// Variables to store the data
const char *feedTime;
int nodeOrder[4];
int ballNode;

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect
  }

  // Initialize SD card
  if (!SD.begin()) {
    Serial.println("Initialization failed!");
    return;
  }

  // Open file for reading
  File file = SD.open(filename);
  if (!file) {
    Serial.println("Error opening file!");
    return;
  }

  // Allocate the JSON document
  // Should be larger than your JSON input
  StaticJsonDocument<200> doc;

  // Deserialize the JSON document
  DeserializationError error = deserializeJson(doc, file);
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }

  // Extract the data
  feedTime = doc["feed_time"];
  JsonArray arr = doc["node_order"];
  for (int i = 0; i < arr.size(); i++) {
    nodeOrder[i] = arr[i];
  }
  ballNode = doc["ball_node"];

  // Close the file
  file.close();

  // Print values to Serial for verification
  Serial.println(feedTime);
  for (int i = 0; i < 4; i++) {
    Serial.println(nodeOrder[i]);
  }
  Serial.println(ballNode);
}

void loop() {
}
