#include <Servo.h>

Servo rightArm;
Servo leftArm;

void setup() {
  Serial.begin(9600);
  rightArm.attach(9); // Right arm servo pin
  leftArm.attach(10); // Left arm servo pin
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');

    if (command == "hi") {
      waveHi();
    } else if (command == "gesture") {
      simpleGesture();
    }
  }
}

void waveHi() {
  for (int i = 0; i < 2; i++) {
    rightArm.write(60);
    delay(500);
    rightArm.write(120);
    delay(500);
  }
  rightArm.write(90); // Reset
}

void simpleGesture() {
  leftArm.write(45);
  rightArm.write(135);
  delay(500);
  leftArm.write(90);
  rightArm.write(90);
}
