#include <Servo.h>

// Define servo objects for each motor.  Adjust the pin numbers!
Servo motor1;
Servo motor2;
Servo motor3;
Servo motor4;
Servo motor5;
Servo motor6;
// ... add more servos as needed for all 18 motors

void setup() {
  Serial.begin(9600);
  // Attach servos to pins.  Use the correct pin numbers for your wiring!
  motor1.attach(2);  // Example: Motor 1 on pin 2
  motor2.attach(3);  // Example: Motor 2 on pin 3
  motor3.attach(4);
  motor4.attach(5);
  motor5.attach(6);
  motor6.attach(7);
  // ... attach the rest of your servos.  You'll have 12 more.
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove лишние пробелы и символы новой строки

    // Parse the command.  The format is "M1=angle1,M2=angle2,..."
    int motor, angle;
    char *token;
    char *str = strdup(command.c_str()); // Create a modifiable copy

    token = strtok(str, ","); // Get first token
    while (token != NULL) {
      if (sscanf(token, "M%d=%d", &motor, &angle) == 2) {
        // Valid command format
        switch (motor) {
          case 1: motor1.write(angle); break;
          case 2: motor2.write(angle); break;
          case 3: motor3.write(angle); break;
          case 4: motor4.write(angle); break;
          case 5: motor5.write(angle); break;
          case 6: motor6.write(angle); break;
          // ... handle the rest of the motors (7 through 18)
          case 7:  motor7.write(angle); break;
          case 8:  motor8.write(angle); break;
          case 9:  motor9.write(angle); break;
          case 10: motor10.write(angle); break;
          case 11: motor11.write(angle); break;
          case 12: motor12.write(angle); break;
          case 13: motor13.write(angle); break;
          case 14: motor14.write(angle); break;
          case 15: motor15.write(angle); break;
          case 16: motor16.write(angle); break;
          case 17: motor17.write(angle); break;
          case 18: motor18.write(angle); break;
        }
      }
      token = strtok(NULL, ","); // Get next token
    }
    free(str);  // Free the allocated memory
  }
}
