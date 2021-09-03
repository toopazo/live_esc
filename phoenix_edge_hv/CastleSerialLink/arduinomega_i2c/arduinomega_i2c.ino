// Wire Master Writer
// by Nicholas Zambetti <http://www.zambetti.com>

// Demonstrates use of the Wire library
// Writes data to an I2C/TWI slave device
// Refer to the "Wire Slave Receiver" example for use with this

// Created 29 March 2006

// This example code is in the public domain.


#include <Wire.h>

int get_checksum(int arr[]){
  int sumarr = arr[0] + arr[1] + arr[2] + arr[3];
  int chk = (0 - sumarr) % 256;
  return chk;
}

void setup()
{
  Wire.begin(); // join i2c bus (address optional for master)
  Wire.setClock(100000);
  Serial.begin(115200);  // start serial for output
  Serial.println("Hello");         // print the character
}

int cnt = 0;

void loop()
{
  int add = 12;
  int reg = 0;
  // d10000 = 00100111 00010000 = d39 d16
  int da0 = 39;
  int da1 = 16 + cnt;  
  int cmdarr[4] = {add, reg, da0, da1};
  int chk = get_checksum(cmdarr);

  //
  Serial.println("Writing..");         // print the character
  //
  Wire.beginTransmission(add); // transmit to device #4
  int reg_data[4] = {reg, da0, da1, chk};
  // Wire.write(reg_data, 4);        // sends four bytes
  Wire.write(reg);
  Wire.write(da0);
  Wire.write(da1);
  Wire.write(chk);  
  Wire.endTransmission();    // stop transmitting

  //
  Serial.println("Reading ..");         // print the character
  //
  Wire.requestFrom(add, 3);    // request 3 bytes from slave device #add

  while (Wire.available()) { // slave may send less than requested
    char c = Wire.read(); // receive a byte as character
    Serial.println(c, DEC);         // print the character
  }
  
  delay(1000);
  Serial.println("next try");         // print the character
  cnt++;

}
