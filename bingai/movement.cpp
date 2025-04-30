#include <Servo.h>

// Define the servos for both arms
Servo rightArm1, rightArm2, rightArm3;
Servo leftArm1, leftArm2, leftArm3;

void setup() {
    Serial.begin(9600);

    // Attach all right arm servos
    rightArm1.attach(9);
    rightArm2.attach(10);
    rightArm3.attach(11);

    // Attach all left arm servos
    leftArm1.attach(6);
    leftArm2.attach(7);
    leftArm3.attach(8);

    // Set initial positions
    rightArm1.write(0); rightArm2.write(0); rightArm3.write(0);
    leftArm1.write(0); leftArm2.write(0); leftArm3.write(0);
}

// Waving hi (Only right arm moves)
void waveHi() {
    for (int pos = 0; pos <= 45; pos += 5) {
        rightArm1.write(pos); rightArm2.write(pos); rightArm3.write(pos); // All right arm servos move together
        delay(100);
    }
    delay(500);
    for (int pos = 45; pos >= 0; pos -= 5) {
        rightArm1.write(pos); rightArm2.write(pos); rightArm3.write(pos);
        delay(100);
    }
}

// Explanation gesture (Both arms move together)
void explainGesture() {
    for (int i = 0; i < 3; i++) {
        rightArm1.write(20); rightArm2.write(20); rightArm3.write(20);
        leftArm1.write(20); leftArm2.write(20); leftArm3.write(20); // Move both arms forward
        delay(500);
        rightArm1.write(0); rightArm2.write(0); rightArm3.write(0);
        leftArm1.write(0); leftArm2.write(0); leftArm3.write(0); // Move both arms back to neutral
        delay(500);
    }
}

// Pointing gesture (Only right arm moves slightly to indicate pointing)
// void pointGesture() {
//     rightArm1.write(30); rightArm2.write(30); rightArm3.write(30);
//     delay(700);
//     rightArm1.write(0); rightArm2.write(0); rightArm3.write(0);
// }

void loop() {
    if (Serial.available() > 0) {
        char command = Serial.read();
        if (command == '1') {
            waveHi();  // Right arm waves
        } else if (command == '2') {
            explainGesture();  // Both arms move to simulate explanation
        } //else if (command == '3') {
            //pointGesture();  // Right arm points
        //}
    }
}
