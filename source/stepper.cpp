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

ISR(TIMER2_COMPA_vect){

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


#ifdef __CUT__
char Step(long *delta, char rapid, long *feedPerSec)
{
  /* Z only */
  long steps[3] = { 0, 0, 0 };
  long sleeptime = 230;

  DEBUG("STEPS:   %ld", delta[2]);
  steps[2] = delta[2] * 100 / stepDist[2];

  DEBUG("Z STEPS:   %ld,   rapid = %d", steps[2], rapid);
  DEBUG("stepDist[2]:   %ld,   rapid = %d", steps[2], rapid);
  /* set direction */
  digitalWrite(dirPin, (steps[2] < 0) ? 1 : 0);
  steps[2] = abs(steps[2]);
  delayMicroseconds(10);

  /* RAMP UP */
  int accelleration = 1;
  int minDelay = 100;
  int maxDelay = 230;
  int delay = maxDelay;

  if (! rapid) { 
    accelleration = 0;
  }

  /* ramp up */
  char stopping = 0;
  for (long s = 0; s < steps[2]; s++) {
    /* recalculate delay */
    if (((accelleration > 0) && delay > minDelay) ||
	((accelleration < 0) && delay < minDelay)) {
      delay = delay - accelleration;
    }
    digitalWrite(stepPin, 1);
    delayMicroseconds(delay); 
    digitalWrite(stepPin, 0);
    delayMicroseconds(delay); 
    
    if (! stopping && (abs(steps[2] - s) < (maxDelay - minDelay))) {
      //      DEBUG("STOPPING! s = %ld\n", s);
      /* start decellerating */
      stopping = 1;
      accelleration = -accelleration;
    }
  }
}
#endif
