#include <Arduino.h>
#include "cnc.h"

volatile long int_counter = 0;
volatile long last_pulse = 0;  // when was the last step issued

volatile long steps_left = 0;  // number of steps left in this movement
volatile char is_moving = 0;   // enables / disables the step generation

volatile long targetDelay = 0;
volatile long curDelay = 0;
volatile long maxDelay = 1500;

volatile long accelleration = 10;
volatile long speedLastUpdate = 0;

volatile char negativeMovement = 0;

/* update speed a maximum of 50 times per second */
volatile long timeBetweenAccChange = 1000000/500;


/* interrupt function to increase int_counter */
char movingState = S_STOP;
volatile long accSteps = 0;
volatile long decSteps = 0;

ISR(TIMER2_COMPA_vect)
{
  /* Check if we're moving. If yes, see if enough time has 
     passed since last pulse, and if yes, pulse again */

  if (last_pulse == 0) {
    last_pulse = micros();
  }

  if (is_moving) {
    int_counter++;

    /* three states"
       accellerating
       steady speed
       decellerating */
    long m = micros();

    if (movingState == S_ACC) {
      /* recalculate delay if applicable */
      if (curDelay > targetDelay) {
	/* still accellerating */

	/* see if we should accellerate */
	if ((speedLastUpdate + timeBetweenAccChange) < m) {
	  /* Timer has expired - lets increase the speed */
	  curDelay -= accelleration;
	  speedLastUpdate = m;
	}
      } else {
	/* pin to target delay */
	curDelay = targetDelay;
	movingState = S_STEADY;
      }
    } 

    if (movingState == S_DEC) {
      /* Decellerating */
      if (curDelay < targetDelay) {
	/* still decellarting */

	/* see if we should accellerate */
	if ((speedLastUpdate + timeBetweenAccChange) < m) {
	  /* Timer has expired - lets decrease the speed */
	  curDelay += accelleration;
	  speedLastUpdate = m;
	}
      } else {
	/* pin to target delay */
	curDelay = targetDelay;
      }
    }

    if (abs(last_pulse - m) > curDelay) {
      last_pulse = m;
      if (steps_left > 0) {
	/* Move a step */
	digitalWrite(stepPin, 1);
	digitalWrite(stepPin, 0);
	steps_left --;

	if (movingState == S_ACC) {
	  /* record how many steps were spent accellerating */
	  accSteps++;
	}
	if (movingState == S_DEC) {
	  /* record how many steps were spent accellerating */
	  decSteps++;
	}
	
	/* update global step counter */
	if (negativeMovement) {
	  pos.z --;
	} else {
	  pos.z ++;
	}

	/* Figure out if we should start decellerating */
	if (steps_left <= accSteps) {
	  /* time to start slowing down! */
	  movingState = S_DEC;
	  targetDelay = maxDelay;
	}
      }
      else {
	// We've run out of steps - stop moving
	is_moving = 0;
      }
    }
  }
}


/* Immediately stop moving if currently moving */
void EmergencyStop()
{
  is_moving = 0;
}


char Step(long actualSteps, float stepsPerSec)
{
  negativeMovement = (actualSteps < 0) ? 1 : 0;

  /* set direction */
  digitalWrite(dirPin, (actualSteps < 0) ? 1 : 0);
  long totSteps = abs(actualSteps);
  delayMicroseconds(10);

  /* Calculate target delay between steps */
  float stepDelay = 1000000.0 / stepsPerSec;

  DEBUGFLOAT("#### stepDelay", stepDelay);
  
  while (is_moving) {
    ; // busy wait 
  }

  /* This bit submits the command, in effect */
  targetDelay = (long)stepDelay;
  curDelay = maxDelay;
  
  accSteps = 0;
  decSteps = 0;
  steps_left = totSteps;
  is_moving = 1; /* this enables the interrupt if statement */
  movingState = S_ACC;

  return 0;
}

