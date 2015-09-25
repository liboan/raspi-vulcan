#include <Servo.h>

Servo a;

void setup() {
  a.attach(10); //port 10: servo 1 on the motor shield
  Serial.begin(9600);
}

int pos = 90;
long lasttime = 0;
int delta = 0;

byte input;

void loop() {
  delta = millis() - lasttime;
  input = Serial.read();
  int spd = (int)input - 90; //RPi master sends speed values b/w 0 and 180, scale so 90 is stopped
  Serial.print(input);
  Serial.print("\t");
  Serial.print(spd);
  Serial.print("\t");
  Serial.println(pos);
  if (delta > 100) { //master's speed commands = degrees/100 ms
    lasttime = millis();
    pos = max(0, min(pos + spd, 180)); //keep b/w 0 and 180  
    a.write(pos);
  }
}
