

extern volatile long steps_left;
extern volatile unsigned long last_pulse;
extern volatile char is_moving;

extern char Step(long actualSteps, float stepsPerSec);
extern void EmergencyStop();


extern volatile long maxDelay;
extern volatile long accelleration;
