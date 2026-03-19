// VT LUNA Rover - Arduino Motor Control
// Controls 5 Cytron MD30C motor drivers and 3 servos
// Gets commands from Raspberry Pi over Serial at 115200 baud
//
// Motor layout (top view):
//   M1 Front-Left    M3 Front-Right
//   M2 Rear-Left     M4 Rear-Right
//   M5 Mechanism motor
//
// Each Cytron MD30C only needs 2 pins: PWM (speed) and DIR (direction)
//
// Commands the Pi sends over Serial:
//   DRIVE:left,right   speeds from -255 to 255
//   MECH:speed         mechanism motor, -255 to 255
//   SERVO:s1,s2,s3     three servo angles, 0 to 180
//   STOP               stop everything
//   PING               health check, Arduino replies PONG

#include <Servo.h>

// Motor pins: each driver gets a PWM pin and a DIR pin
int M1_PWM = 2;   int M1_DIR = 22;  // Front-Left
int M2_PWM = 3;   int M2_DIR = 23;  // Rear-Left
int M3_PWM = 4;   int M3_DIR = 24;  // Front-Right
int M4_PWM = 5;   int M4_DIR = 25;  // Rear-Right
int M5_PWM = 6;   int M5_DIR = 26;  // Mechanism

// Servo pins
int SERVO1_PIN = 9;
int SERVO2_PIN = 10;
int SERVO3_PIN = 11;

Servo servo1;
Servo servo2;
Servo servo3;

// Serial reading
String inputBuffer = "";
bool cmdReady = false;

// Watchdog timer - stops motors if Pi goes quiet for 500ms
unsigned long lastCmdTime = 0;
unsigned long WATCHDOG_MS = 500;

void setup() {
  Serial.begin(115200);

  // Set all motor pins as outputs
  pinMode(M1_PWM, OUTPUT); pinMode(M1_DIR, OUTPUT);
  pinMode(M2_PWM, OUTPUT); pinMode(M2_DIR, OUTPUT);
  pinMode(M3_PWM, OUTPUT); pinMode(M3_DIR, OUTPUT);
  pinMode(M4_PWM, OUTPUT); pinMode(M4_DIR, OUTPUT);
  pinMode(M5_PWM, OUTPUT); pinMode(M5_DIR, OUTPUT);

  // Attach servos and center them at startup
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);
  servo1.write(90);
  servo2.write(90);
  servo3.write(90);

  stopAll();

  Serial.println("READY:VT_LUNA_ROVER");
}

void loop() {
  // Run the command if we got a full line
  if (cmdReady) {
    parseCommand(inputBuffer);
    inputBuffer = "";
    cmdReady = false;
  }

  // Stop motors if we havent heard from the Pi in a while
  if (millis() - lastCmdTime > WATCHDOG_MS) {
    stopAll();
  }
}

// Build up the command string one character at a time
void serialEvent() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') {
      cmdReady = true;
    } else {
      inputBuffer += c;
    }
  }
}

// Figure out what command came in and run it
void parseCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  lastCmdTime = millis();

  int colon = cmd.indexOf(':');
  String key = (colon >= 0) ? cmd.substring(0, colon) : cmd;
  String val = (colon >= 0) ? cmd.substring(colon + 1) : "";

  if (key == "DRIVE") {
    int comma = val.indexOf(',');
    if (comma < 0) { Serial.println("ERR:DRIVE_FMT"); return; }
    int leftSpeed  = constrain(val.substring(0, comma).toInt(), -255, 255);
    int rightSpeed = constrain(val.substring(comma + 1).toInt(), -255, 255);
    setMotor(M1_PWM, M1_DIR, leftSpeed);
    setMotor(M2_PWM, M2_DIR, leftSpeed);
    setMotor(M3_PWM, M3_DIR, rightSpeed);
    setMotor(M4_PWM, M4_DIR, rightSpeed);
    Serial.println("OK:DRIVE");
  }

  else if (key == "MECH") {
    int speed = constrain(val.toInt(), -255, 255);
    setMotor(M5_PWM, M5_DIR, speed);
    Serial.println("OK:MECH");
  }

  else if (key == "SERVO") {
    int c1 = val.indexOf(',');
    int c2 = val.indexOf(',', c1 + 1);
    if (c1 < 0 || c2 < 0) { Serial.println("ERR:SERVO_FMT"); return; }
    servo1.write(constrain(val.substring(0, c1).toInt(), 0, 180));
    servo2.write(constrain(val.substring(c1 + 1, c2).toInt(), 0, 180));
    servo3.write(constrain(val.substring(c2 + 1).toInt(), 0, 180));
    Serial.println("OK:SERVO");
  }

  else if (key == "STOP") {
    stopAll();
    Serial.println("OK:STOP");
  }

  else if (key == "PING") {
    Serial.println("PONG");
  }

  else {
    Serial.println("ERR:UNKNOWN");
  }
}

// Drive a single Cytron MD30C motor
// speed: positive = forward, negative = reverse, 0 = stop
void setMotor(int pwmPin, int dirPin, int speed) {
  if (speed > 0) {
    digitalWrite(dirPin, HIGH);
    analogWrite(pwmPin, speed);
  } else if (speed < 0) {
    digitalWrite(dirPin, LOW);
    analogWrite(pwmPin, -speed);
  } else {
    digitalWrite(dirPin, LOW);
    analogWrite(pwmPin, 0);
  }
}

// Stop all 5 motors
void stopAll() {
  setMotor(M1_PWM, M1_DIR, 0);
  setMotor(M2_PWM, M2_DIR, 0);
  setMotor(M3_PWM, M3_DIR, 0);
  setMotor(M4_PWM, M4_DIR, 0);
  setMotor(M5_PWM, M5_DIR, 0);
}
