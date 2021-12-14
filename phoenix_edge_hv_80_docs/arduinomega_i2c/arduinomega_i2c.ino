// Wire Master Writer
// by Nicholas Zambetti <http://www.zambetti.com>

// Demonstrates use of the Wire library
// Writes data to an I2C/TWI slave device
// Refer to the "Wire Slave Receiver" example for use with this

// Created 29 March 2006

// This example code is in the public domain.


#include <Wire.h>

int get_checksum(byte arr[]){
  byte sumarr = arr[0] + arr[1] + arr[2] + arr[3];
  // byte chk = (0 - sumarr) % 256;
  byte chk = (0 - sumarr);
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
byte res = 0;

void loop()
{
  byte add = 12;
  byte reg = 1;
  // d10000 = 00100111 00010000 = d39 d16
  // byte da1 = 39;
  // byte da0 = (16 + cnt);
  byte da1 = 100 * 0;
  byte da0 = (100 + cnt) * 0;
  byte cmdarr[4] = {add, reg, da1, da0};
  byte chk = get_checksum(cmdarr);

  //
  Serial.println("Calling Wire.beginTransmission ..");
  //
  Wire.beginTransmission(add); // transmit to device in write mode
  byte reg_data[4] = {reg, da0, da1, chk};
  // Wire.write(reg_data, 4);        // sends four bytes
  Wire.write(reg);
  Wire.write(da1);
  Wire.write(da0);
  Wire.write(chk);  
  res = Wire.endTransmission(true);    // stop transmitting

  Serial.print("add ");
  Serial.println(add);
  Serial.print("reg ");
  Serial.println(reg);
  Serial.print("da1 ");
  Serial.println(da1);
  Serial.print("da0 ");
  Serial.println(da0);
  int dat = (da1)<<8 | da0; 
  Serial.print("da1da0 ");
  Serial.println(dat);
  Serial.print("chk ");
  Serial.println(chk);
  Serial.print("res ");
  Serial.println(res);

  //
  Serial.println("Calling Wire.requestFrom ..");
  //
  res = Wire.requestFrom(add, 3, true);    // request 3 bytes from slave device #add
  Serial.print("res ");
  Serial.println(res);

  while (Wire.available()) { // slave may send less than requested
    int c = Wire.read(); // receive a byte as character
    Serial.print("byte ");
    Serial.println(c);
  }
  
  delay(5000);
  Serial.println("next try");         // print the character
  cnt++;

}
