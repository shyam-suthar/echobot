#include <Servo.h>

// Create an array to store 20 Servo objects
Servo servos[20];
int servoPins[20] = {
  2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
  12, 13, 14, 15, 16, 17, 18, 19, 20, 21
};

// Stores the current positions
int servoPosition[20];

// Sets up the servo pins and moves to initial position
void setup() {
  Serial.begin(9600);

  // Attach all servos to the defined pins
  for (int i = 0; i < 20; i++) {
    servos[i].attach(servoPins[i]);
  }

  delay(500);
  initialPosition();
}

// Loop listens for Raspberry Pi commands
void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    if (command == '1') {
      sayHi(2, 700); // Wave hi 2 times
    } else if (command == '2') {
      explanationGesture(); // Perform a gesture while responding
    }
  }
}

// Moves servos to a position smoothly
void moveServos(int target[], int duration) {
  float increment[20];
  for (int i = 0; i < 20; i++) {
    increment[i] = (target[i] - servoPosition[i]) / (duration / 10.0);
  }

  unsigned long finalTime = millis() + duration;
  for (int step = 1; millis() < finalTime; step++) {
    unsigned long partialTime = millis() + 10;
    for (int i = 0; i < 20; i++) {
      servos[i].write((int)(servoPosition[i] + (step * increment[i])));
    }
    while (millis() < partialTime);
  }

  for (int i = 0; i < 20; i++) {
    servoPosition[i] = target[i];
  }
}

// Default starting position
void initialPosition() {
  int pose[20] = {
    90, 150, 150, 30, 90, 90, 90, 30, 30, 150,
    90, 90, 30, 30, 30, 150, 150, 150, 90, 90
  };
  moveServos(pose, 2000);
}

// Wave hand for "hi" gesture
void sayHi(int count, int speed) {
  int upPose[20] = {
    90, 150, 150, 30, 90, 90, 90, 30, 30, 150,
    90, 90, 180, 90, 90, 150, 150, 150, 90, 90
  };
  moveServos(upPose, speed * 2);

  for (int i = 0; i < count; i++) {
    int wave1[20] = {
      90, 150, 150, 30, 90, 90, 90, 30, 30, 150,
      90, 90, 180, 90, 60, 150, 150, 150, 90, 90
    };
    int wave2[20] = {
      90, 150, 150, 30, 90, 90, 90, 30, 30, 150,
      90, 90, 180, 90, 120, 150, 150, 150, 90, 90
    };
    moveServos(wave1, speed);
    moveServos(wave2, speed);
  }

  initialPosition();
}

// Simple explanation movement (like nod or hand movement)
void explanationGesture() {
  int gesture1[20] = {
    90, 150, 150, 30, 90, 90, 90, 30, 30, 150,
    90, 90, 50, 90, 90, 150, 150, 150, 90, 90
  };
  int gesture2[20] = {
    90, 150, 150, 30, 90, 90, 90, 30, 30, 150,
    90, 90, 30, 90, 90, 150, 150, 150, 90, 90
  };

  moveServos(gesture1, 700);
  moveServos(gesture2, 700);

  initialPosition();
}
