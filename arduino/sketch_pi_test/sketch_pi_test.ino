void setup() {
  Serial.begin(9600);
}

byte n;

void loop() {
  // n = (n + 1) % 255;
  //Serial.write(n);
  if (Serial.available() > 0) {
    n = Serial.read();
    Serial.println(n, DEC);
  }
  
}
