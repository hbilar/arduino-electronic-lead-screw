
#include <Arduino.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>


#include "cnc.h"
#include "stepper.h"
#include "hall_sensor.h"


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

char hallPin = 2; /* Pin for the rpm hall sensor */

int simulatedRPMDelay = 500;


char stepPinBit = B00010000;  /* pin 12 is bit 5 in PORTB */
char dirPinBit =  B00001000;  /* pin 11 is bit 4 in PORTB */

/* globals */
volatile t_pos pos;   // tool position
volatile t_rotation spindle; // spindle related stuff
t_feed z_feed;      // settings for movement speed when feeding (cutting)
t_feed z_travel_feed; // settings for movement when travelling (not cutting)
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


void SetZero()
{
  DEBUG("Setting zero point here");
  pos.z = 0;
}


void SetFeedType(char *feed_type) 
{
  DEBUG("SetFeedType(feed_type = %s):", feed_type);

  if (streq(feed_type, "rot")) {
    DEBUG("Setting rotational based move type (mm/revolution)");
    z_feed.current_move_type = movement_rotational_based;
  }
  else if (streq(feed_type, "time")) {
    DEBUG("Setting time based move type (mm/minute)");
    z_feed.current_move_type = movement_time_based;
  }
  else {
    DEBUG("ERROR: Invalid feed type specified")
  }
}


void MoveRelative(float distance, t_feed feed)
{
  float stepsForDistance = z_screw.stepsPerRev * distance / z_screw.pitch;
  long actualSteps = roundf(stepsForDistance);

  DEBUGFLOAT("MoveRelative(distance =): ", distance);
  DEBUGFLOAT("stepsForDistance: ", stepsForDistance);
  DEBUG("actualSteps = %d", actualSteps);

  /* feed rate */
  float s = distance;
  float v = 0;
  if (feed.current_move_type == movement_time_based ) {
    v = feed.feedMmPerMin / 60;   // mm / s 
  } else {
    v = feed.feedMmPerRot * spindle.rpm / 60;   // mm / s 
  }
  float t = s / v;
  //  float v_steps_per_sec = v * z_screw.stepsPerMM;
  float v_steps_per_sec;
  RecalcStepRate(&v, &v_steps_per_sec);

  DEBUGFLOAT("s(mm) = ", s);
  DEBUGFLOAT("v(mm/s) = ", v);
  DEBUGFLOAT("v(m/min) = ", v*60/1000.0);
  DEBUGFLOAT("t = ", t);
  DEBUGFLOAT("v_steps_per_sec = ", v_steps_per_sec);

  Step(actualSteps, v_steps_per_sec);
}


void MoveAbsolute(float new_pos, t_feed feed)
{
  /* find current position, and then figure out how to move to get to the
     absolute position required */

  float stepsFromZero = z_screw.stepsPerRev * new_pos / z_screw.pitch;
  long actualSteps = roundf(stepsFromZero) - pos.z;

  DEBUGFLOAT("MoveAbsolute(new_pos =): ", new_pos);
  DEBUG("actualSteps = %d", actualSteps);

  /* feed rate */
  float s = new_pos;
  float v = feed.feedMmPerMin / 60;   // mm / s 

  float t = s / v;
  float v_steps_per_sec; /* this is how many pulses per second to send to the stepper */
  RecalcStepRate(&v, &v_steps_per_sec);


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
    /* scan forward in userBuf until we find end of string, a new line or space */
    while (*p && *p != ' ' && *p != '\r') {
      p++;
    }

    /* If we are not at end of string, and the current char is a space or new line, insert
    an end of string marker */
    if (*p && (*p == ' ' || *p == '\r')) {
      *p++ = (char)NULL;
    }

    /* If we're at end of string in userBuf, then break out from the loop */
    if (! *p) {
      break;
    }
  }

  /*
  DEBUG("PARAMS: n = %d", '\n');
  for (char n = 0; n < NUM_ARGS; n++) {
    if (params[n]) {
      DEBUG(">>%s<<", params[n]);
    }
  }
  */
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
    else if (streq(params[0], "zero")) {
      /* Set zero point */
      SetZero();
    } 
    else if (streq(params[0], "feedtype")) {
      /* Set move type */
      SetFeedType(params[1]);
    } 
    /* Relative movements */
    else if (streq(params[0], "feedrel")) {
      float newZ = atof(params[1]);
      MoveRelative(newZ, z_feed);
    }
    else if (streq(params[0], "travelrel")) {
      float newZ = atof(params[1]);
      MoveRelative(newZ, z_travel_feed);
    }
    /* absolute movements */
    else if (streq(params[0], "feedabs")) {
      float newZ = atof(params[1]);
      MoveAbsolute(newZ, z_feed);
    }
    else if (streq(params[0], "travelabs")) {
      float newZ = atof(params[1]);
      MoveAbsolute(newZ, z_travel_feed);
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
    else if (streq(params[0], "travelspeed")) {
      float newF = fabs(atof(params[1]));
      z_travel_feed.feedMmPerMin = newF;
      DEBUGFLOAT("New travel rate (mm/min): ", newF);
    }
    else if (streq(params[0], "s")) {
      float newRpm = fabs(atof(params[1]));
      spindle.rpm = newRpm; 
      //      spindle.rps = spindle.rpm / 60;
      DEBUGFLOAT("New RPM: ", spindle.rpm);
    }
    else if (streq(params[0], "d")) {
      simulatedRPMDelay = abs(atoi(params[1]));
      DEBUG("New RPM delay: %d", simulatedRPMDelay);
    }
    else if (streq(params[0], "t")) {
      //simulatedRPMDelay = abs(atoi(params[1]));
      is_threading = ! is_threading;
      DEBUG("Threading mode: %d", is_threading);
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
  z_screw.pitch = 3.0 * 32.0 / 50.0; // including gearing from pulleys 
  z_screw.stepsPerRev = 800;
  z_screw.stepsPerMM = z_screw.stepsPerRev / z_screw.pitch;

  /* spindle related */
  // TODO: Fix RPM detection
  spindle.rpm = 200; 

  z_feed.feedMmPerRot = 3.0*32.0/50.0; //mm per rev
  //z_feed.feedMmPerRot = 3.0; //mm per rev
  z_feed.feedMmPerMin = 2.0 * 60; // mm / s
  z_feed.current_move_type = movement_time_based;

  // travel speed
  z_travel_feed.feedMmPerMin = 500.0; // 200mm / min
  z_travel_feed.feedMmPerRot = 1.0; // this is not used, but initialized anyway
  z_travel_feed.current_move_type = movement_time_based;
  

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

  /* Attach the RPM interrupt to the hall sensor pin */
  attachInterrupt(digitalPinToInterrupt(hallPin), 
		  rpmInterrupt, FALLING);

  SendUser("");
  SendUser("Simple Electronic Lead Screw");
  SendUser("");
  SendUser(prompt);
}


/* vars to keep time stamps. 
mp = time the last rpm update was sent to the user.
m = last time an rpmInterrupt was sent */
long m = 0;
long mp = 0;

void loop()
{
  if (PollUserData()) {
    /* There's a complete function to handle */
    ProcessCommand();
  }

  /* calculate rpm for threading and adjust the step delay */
  if (is_threading) {
    long m1 = millis();

    /* this bit simulates an RPM measurement. the rpmInterrupt is called
       every simulatedRPMDelay milliseconds */
    if (abs(m - m1) > simulatedRPMDelay) {
      float r = calculateRPM();
      spindle.rpm = r;
    
      /* recalc step rate to keep spindle / thread synched */
      float v_steps_per_sec;
      float v = z_feed.feedMmPerRot * spindle.rpm / 60; // mm / s 
      RecalcStepRate(&v, &v_steps_per_sec);
      SetTargetDelay(&v_steps_per_sec);
    
      rpmInterrupt();

      if (abs(mp - m1) > 1000) {
      	mp = m1;
      	DEBUGFLOAT("current RPM value = ", r);
      }
      m = m1;
    }
  }
}
