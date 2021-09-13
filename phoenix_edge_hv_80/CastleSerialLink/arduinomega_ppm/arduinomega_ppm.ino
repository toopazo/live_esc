// #include <PulsePosition.h>
// #include <PPMEncoder.h>
#include <Servo.h>


Servo myservo;  // create servo object to control a servo
byte mbyte = 0;
int mint = 0;
// PulsePositionOutput myOutput;
int txPin = 10;

void setup() {
  Serial.begin(115200); 
  // ppmEncoder.begin(txPin, 1);
  myservo.attach(9);
  // myOutput.begin(txPin); 
}


void loop() {

  // reply only when you receive data:
  if (Serial.available() > 0) {
    Serial.print("I received: ");
    //mbyte = Serial.read();
    // Serial.println(mbyte, DEC);
    mint = Serial.parseInt(SKIP_ALL);
    Serial.println(mint, DEC);

    mint = constrain(mint, 0, 100);
    
  
    // ppmEncoder.setChannel(0, 2500);
    // ppmEncoder.setChannel(0, PPMEncoder::MAX);
    // ppmEncoder.setChannelPercent(0, mint);
  
    // myservo.write(mint);
    int msec = mint * 10 + 1000;
    myservo.writeMicroseconds(msec);
  
    // float microseconds = mint * 10 + 1000;
    // myOutput.write(1, microseconds); 

  }
  delay(3000);
}
