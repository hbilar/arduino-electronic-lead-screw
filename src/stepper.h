

extern volatile long steps_left;
extern volatile unsigned long last_pulse;
extern volatile char is_moving;
extern volatile char is_threading;

extern char Step(long actualSteps, float stepsPerSec);
extern void EmergencyStop();
extern void RecalcStepRate(float *v, float *v_steps_per_sec);
extern void SetTargetDelay(float *stepsPerSec);


extern volatile long maxDelay;
extern volatile long accelleration;
