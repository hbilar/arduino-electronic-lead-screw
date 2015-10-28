
#include <stdbool.h>
#include <string.h>
#include <stdio.h>


#include "cnc.h"
#include "stepper.h"


/* user comms related */
const int serialBps = 9600;

#define NUM_ARGS 4
#define BUF_SIZE 50
char *prompt = "> ";
char userBuf[BUF_SIZE] = "";
char *userBufPtr = userBuf;
char *params[NUM_ARGS];

#define CLEARBUFFER { memset(userBuf, 0, sizeof(userBuf)); userBufPtr = userBuf; }

/* data pins */
const int ledPin = 13;
char stepPin = 12;
char dirPin = 11;

char stepPinBit = B00010000;  /* pin 12 is bit 5 in PORTB */
char dirPinBit =  B00001000;  /* pin 11 is bit 4 in PORTB */

/* globals */
volatile t_pos pos;   // tool position
volatile t_rotation spindle; // spindle related stuff
t_feed z_feed; 
t_leadscrew z_screw; 


/* Abstraction to send a string of text to the user. Might be better to use 
   an ellipsis function (... operator) to pass variable numbers of parameters */
void SendUser(char *buf) {
  Serial.println(buf);
}


void SendPos()
{
  float relDist = pos.z * z_screw.pitch / z_screw.stepsPerRev;
 
  DEBUG("==============");
  DEBUG("Global Step Counter:  %d\n", pos.z);
  DEBUGFLOAT("Z Pos: ", relDist);
  DEBUGFLOAT("Z screw pitch (mm): ", z_screw.pitch);
  DEBUGFLOAT("Z steps per rev: ", z_screw.stepsPerRev);
  DEBUGFLOAT("stepsPerMM: ", z_screw.stepsPerMM);
  DEBUGFLOAT("RPM: ", spindle.rpm);
  DEBUG("");
  DEBUG("is_moving: %d", is_moving);
  if (is_moving) {
    DEBUG("steps_left  %ld", steps_left);
    DEBUG("last_pulse  %ld", last_pulse);
  }
}


void SendRPM()
{
  DEBUGFLOAT("RPM: ", spindle.rpm);
}


void MoveRelative(float distance, char timeBased)
{
  float stepsForDistance = z_screw.stepsPerRev * distance / z_screw.pitch;
  long actualSteps = roundf(stepsForDistance);

  DEBUGFLOAT("MoveRelative(distance =): ", distance);
  DEBUGFLOAT("stepsForDistance: ", stepsForDistance);
  DEBUG("actualSteps = %d", actualSteps);

  /* feed rate */
  float s = distance;
  float v = 0;
  if (timeBased) {
    v = z_feed.feedMmPerMin / 60;   // mm / s 
  } else {
    //    v = z_feed.feedMmPerRot * spindle.rps;   // mm / s 
    v = z_feed.feedMmPerRot * spindle.rpm / 60;   // mm / s 
  }
  float t = s / v;
  float v_steps_per_sec = v * z_screw.stepsPerMM;

  DEBUGFLOAT("s(mm) = ", s);
  DEBUGFLOAT("v(mm/s) = ", v);
  DEBUGFLOAT("v(m/min) = ", v*60/1000.0);
  DEBUGFLOAT("t = ", t);
  DEBUGFLOAT("v_steps_per_sec = ", v_steps_per_sec);

  Step(actualSteps, v_steps_per_sec);
}


void BuildParams()
{
  char *p = userBuf;
  memset(params, 0, sizeof(char*) * NUM_ARGS);
  
  for (char n = 0; n < NUM_ARGS; n++) {
    params[n] = p;
    while (*p && (*p != ' ')) {
      p++;
    }
    if (*p && (*p == ' ')) {
      *p++ = (char)NULL;
    }

    if (! *p) {
      /* End of string */
      break;
    }
  }

  /*  DEBUG("PARAMS:");
  for (char n = 0; n < NUM_ARGS; n++) {
    if (params[n]) {
      DEBUG(">>%s<<", params[n]);
    }
    }*/
}


void ProcessCommand()
{
    char b[100];
    SendUser(userBuf);
    BuildParams();
    
    /* Go through commands and respond */
    if (streq(params[0], "pos")) {
      /* Tool position */
      SendPos();
    }
    else if (streq(params[0], "rpm")) {
      /* Spindle RPM */
      SendRPM();
    } 
    else if (streq(params[0], "moverpm")) {
      float newZ = atof(params[1]);
      MoveRelative(newZ, 0);
    }
    else if (streq(params[0], "movetime")) {
      float newZ = atof(params[1]);
      DEBUGFLOAT("Time based movement: ", newZ);
      MoveRelative(newZ, 1);
    }
    else if (streq(params[0], "feedraterpm")) {
      float newF = fabs(atof(params[1]));
      z_feed.feedMmPerRot = newF;
      DEBUGFLOAT("New feed rate (mm/rotation): ", newF);
    }
    else if (streq(params[0], "feedratetime")) {
      float newF = fabs(atof(params[1]));
      z_feed.feedMmPerMin = newF;
     DEBUGFLOAT("New time based rate (mm/min): ", newF);
    }
    else if (streq(params[0], "s")) {
      float newRpm = fabs(atof(params[1]));
      spindle.rpm = newRpm; 
      //      spindle.rps = spindle.rpm / 60;
      DEBUGFLOAT("New RPM: ", spindle.rpm);
    }
    else if (streq(params[0], "acc")) {
      long newAcc = abs(atoi(params[1]));
      accelleration = newAcc;
      DEBUG("New acc value: %ld", accelleration);
    }
    else if (streq(params[0], "maxdelay")) {
      maxDelay = abs(atoi(params[1]));
      DEBUG("New max delay value: %ld", maxDelay);
    }
    else if (streq(params[0], "stop")) {
      EmergencyStop();
      DEBUG("Emergency stop button called");
    }
    else {
      /* Unknown command */
      DEBUG("ERR: NOT IMPLEMENTED");
    }

    CLEARBUFFER;
    SendUser(prompt);
}


/* Read data from user, if there is any. If the end of a command is detected
 * (i.e. ; or \n), then return 1, otherwise return 0. */
char PollUserData() {
  if (Serial.available() > 0) {
    // read the incoming byte:
    char incomingByte = Serial.read();

    // save character
    if (incomingByte == '\n' || incomingByte == ';') {
      return 1;
    } else {
      if (userBufPtr < (userBuf + sizeof(userBuf)))
	*userBufPtr++ = incomingByte;
    }
  }
  return 0;
}


void setup() 
{
  /* global position tracker */
  pos.z = 0;

  /* setup screw data */
  z_screw.pitch = 3; 
  z_screw.stepsPerRev = 800;
  z_screw.stepsPerMM = z_screw.stepsPerRev / z_screw.pitch;

  /* spindle related */
  spindle.rpm = 200; 
  //  spindle.rps = spindle.rpm / 60;

  //  z_feed.feedMmPerRot = 0.1; //mm per rev
  z_feed.feedMmPerRot = 3.0; //mm per rev
  z_feed.feedMmPerMin = 12.0 * 60; //mm / s

  /* disable interrupts */
  cli();

  /* set up timers */
  //set timer2 interrupt at 8kHz
  TCCR2A = 0;// set entire TCCR2A register to 0
  TCCR2B = 0;// same for TCCR2B
  TCNT2  = 0;//initialize counter value to 0
  /* 50kHz */
  OCR2A = 40;// = (16*10^6) / (50000*8) - 1 (must be <256)
  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  // Set CS21 bit for 8 prescaler
  TCCR2B |= (1 << CS21);   
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);

  /* enable interrupts */
  sei();

  pinMode(ledPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  Serial.begin(serialBps);

  SendUser("");
  SendUser("Simple Electronic Lead Screw");
  SendUser("");
  SendUser(prompt);
}


void loop()
{
  if (PollUserData()) {
    /* There's a complete function to handle */
    ProcessCommand();
  }
}
