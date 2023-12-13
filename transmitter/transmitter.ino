//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 02_nRF24L01_Test_Receive

// Code source : https://forum.arduino.cc/t/simple-nrf24l01-2-4ghz-transceiver-demo/405123/2 (By Robin2).

//----------------------------------------Including the libraries.
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
//----------------------------------------

// Defines CE and CSN PINs.
#define CE_PIN  9
#define CSN_PIN 10

// Address through which two modules communicate.
const byte Pipe_Address[6] = "00001";

// Variables to hold the data to be received.
// this must match "dataToSend" in the sender.
char dataReceived[32] = ""; 

// Variables to detect new incoming data.
bool newData = false;

// Create an RF24 object as a radio, while also setting the CE and CSN PINs.
RF24 radio(CE_PIN, CSN_PIN);

//________________________________________________________________________________VOID SETUP()
void setup() {
  // put your setup code here, to run once:
  
  Serial.begin(115200);
  Serial.println();
  delay(2000);

  Serial.println("This is the Receiver.");

  // initialize the radio object.
  radio.begin();

  // set the Power Amplifier level.
  // Use "RF24_PA_MIN" or "RF24_PA_LOW" if the distance between nRF24L01 modules is close to each other.
  // Use "RF24_PA_HIGH" or "RF24_PA_MAX" if the distance between nRF24L01 modules is far from each other.
  // For more details, see here : https://github.com/nRF24/RF24/blob/master/RF24.h#L26C1-L26C1
  radio.setPALevel(RF24_PA_LOW);

  // Set the transmission datarate.
  radio.setDataRate(RF24_250KBPS);

  // Set the address to receive data from the sender. The sender must use the same address.
  radio.openReadingPipe(0, Pipe_Address);

  // Set the nRF24L01 module as the receiver.
  radio.startListening();
}
//________________________________________________________________________________

//________________________________________________________________________________VOID LOOP()
void loop() {
  // put your main code here, to run repeatedly:

  // Calling the receive_Data() subroutine.
  receive_Data();

  // Calling the show_Data() subroutine.
  show_Data();
}
//________________________________________________________________________________

//________________________________________________________________________________receive_Data()
// Subroutine for receiving data.
void receive_Data() {
  if (radio.available()) {
    radio.read(&dataReceived, sizeof(dataReceived));
    newData = true;
  }
}
//________________________________________________________________________________

//________________________________________________________________________________show_Data()
// Subroutine for printing the received data to the serial monitor (serial communication).
void show_Data() {
  if (newData == true) {
    Serial.print("Data received : ");
    Serial.println(dataReceived);
    newData = false;
  }
}
//________________________________________________________________________________
//<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

