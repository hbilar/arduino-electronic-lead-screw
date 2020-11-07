#include <Arduino.h>
#include "cnc.h"


const unsigned long MAX_STAMP_AGE = 6000; // ms
const int MAX_STAMPS = 3;
volatile unsigned long timestamps[MAX_STAMPS];
volatile short int curTimestampPos = 0;
volatile unsigned long lastStamp = 0;

void rpmInterrupt(void)
{
  timestamps[curTimestampPos++] = millis();
  if (curTimestampPos >= MAX_STAMPS) {
    curTimestampPos = 0;
  }
  
  lastStamp = millis();
}


float calculateRPM()
{
  unsigned long curTime = millis();
  short numIntervals = 0;

  /* make a copy of relevant data */
  noInterrupts();  // disable interrupts
  short p = curTimestampPos;
  unsigned long ts[MAX_STAMPS];
  memset(ts, 0, sizeof(ts));
  for (int i = 0; i < MAX_STAMPS; i++) {
    ts[i] = timestamps[i];   
  }
  
  /* find applicable timestamps and the top and bottom number */
  unsigned long low = 0;
  unsigned long high = 0;
  short datapoints = 0;
  for (int i = 0; i < MAX_STAMPS; i++) {
      unsigned long tsDiff = abs((long)curTime - (long)(ts[i]));
      if (tsDiff < MAX_STAMP_AGE) {
        datapoints ++;
        if ((low == 0) || ts[i] <= low) {
          low = ts[i];
        } 
        if (ts[i] > high) {
          high = ts[i];
        }    
    }
  }
  interrupts();    // enable interrupts
  
  
  /*  Serial.print("datapoints: ");
  Serial.println(datapoints);
  Serial.print("low: ");
  Serial.println(low);
  Serial.print("high: ");
  Serial.println(high); */

  float rpm = 0;  
  if (datapoints > 1) {
    unsigned long timeDiff = abs(high - low);
    int revs = datapoints - 1;
    
    float rps = (revs / (timeDiff / 1000.0));
    rpm = (rps * 60.0);       
  }
    
  return rpm;
}
