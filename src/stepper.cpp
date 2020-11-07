#include <Arduino.h>
#include "cnc.h"

volatile unsigned long last_pulse = 0;  // when was the last step issued

volatile long steps_left = 0;  /* number of steps left in 
				  this movement */
volatile char negativeMovement = 0; /* keep track of what 
				       direction we're moving */
volatile char is_moving = 0;   /* enables / disables the
				  step generation */
volatile char is_threading = 0;

/* Notes on targetDelay and accelleration values: 

   if maxdelay is larger than targetdelay, then 
   accelleration / decelleration takes place. 
     
   if maxdelay is smaller than targetdelay, no 
   accelleration / decelleration takes place.
     
   To make slow feeds invoke the acc/dec code, increase 
   maxDelay. To make the accelleration slower/faster
   decrease/increase the accelleration value.
*/


volatile long targetDelay = 0;
volatile long curDelay = 0;
volatile long maxDelay = 1500;
volatile long accelleration = 10;

/* what microsecond was the speed last updated (acc/dec) */
volatile unsigned long speedLastUpdate = 0;

/* update speed a maximum of 500 times per second. Specifies
 microseconds between speed updates */
volatile long timeBetweenAccChange = 1000000/500;


/* interrupt function to move the stepper. This function is called once
   for each clock underflow (50khz), but keeps its own timers for when
   the next pulse should be sent.
   Once the internal pulse timer expires, a pulse is sent and the timer
   is reset */
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
    /* three states:
        accellerating
        steady speed
        decellerating
    */
    unsigned long m = micros();

    /* Check if m < last_pulse. If yes, we have overflowed
       the counter */
    if (m < last_pulse) {
      last_pulse = 0; /* This introduces a small error on
			 overflow, but should be close enough
			 (max error = 1/50000 s) */
    }

    /* This section of the code deals with changing the 
       time between pulses (i.e. accelleration and 
       decelleration). It could be merged into one 
       if statement, but they're kept separate to aid 
       readability at the moment */
    if (movingState == S_ACC) { /* Accellerating */
      if (curDelay > targetDelay) {
        /* We haven't hit target "speed" */
        /* see if we should accellerate */
        if ((speedLastUpdate + timeBetweenAccChange) < m) {
          /* Timer has expired - lets increase the speed */
          curDelay -= accelleration;
          speedLastUpdate = m;
        }
      } else {
        /* pin to target delay */
        curDelay = targetDelay;
        movingState = S_STEADY;  /* record the new state */
      }
    } 
    if (movingState == S_DEC) {  /* Decellerating */
      if (curDelay < targetDelay) {
        /* We haven't hit target "speed" */
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

      if (movingState == S_STEADY) {
        /* in case of threading, adjust speed */
        curDelay = targetDelay;
      }

      /* This section of the code deals with actually moving
        the stepper motor */
      if ((m - last_pulse) > curDelay) {
        last_pulse = m;
        if (steps_left > 0) {
          /* Move a step */
          /*	digitalWrite(stepPin, 1);
            digitalWrite(stepPin, 0); */
          /* Toggle the step pin high, then low without using digitalWrite */
          PORTB = PORTB | stepPinBit;
          steps_left --;
          PORTB = PORTB & (B11111111 ^ stepPinBit);

          if (movingState == S_ACC) {
            /* record how many steps were spent accellerating */
            accSteps++;
          }
          if (movingState == S_DEC) {
            /* record how many steps were spent decellerating */
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
            /* time to start slowing down! This section assumes
              that we spend the same amount of time decellerating
              (i.e. number of steps) as accellerating. */
            movingState = S_DEC;
            targetDelay = maxDelay;
          }
        }
      else {
        /* We've run out of steps - stop moving */
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


void RecalcStepRate(float *v, float *v_steps_per_sec)
{
  *v_steps_per_sec = *v * z_screw.stepsPerMM;  
}


void SetTargetDelay(float *stepsPerSec)
{
  long delay;
  targetDelay = (long)(1000000.0 / *stepsPerSec);
  //  DEBUG("#### targetDelay = %ld", targetDelay);
}


char Step(long actualSteps, float stepsPerSec)
{
  negativeMovement = (actualSteps < 0) ? 1 : 0;

  /* set direction */
  digitalWrite(dirPin, (actualSteps < 0) ? 1 : 0);
  long totSteps = abs(actualSteps);
  delayMicroseconds(10);

  while (is_moving) {
    ; // busy wait 
  }

  /* Calculate target delay between steps */
  SetTargetDelay(&stepsPerSec);
 
  curDelay = maxDelay;
  
  accSteps = 0;
  decSteps = 0;
  steps_left = totSteps;
  is_moving = 1; /* this enables the interrupt if statement */
  movingState = S_ACC;

  return 0;
}

