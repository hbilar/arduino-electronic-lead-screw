
#define DEBUG(format, ...)  { char b[100]; snprintf(b, 100, format, ##__VA_ARGS__); SendUser(b); }
#define DEBUGFLOAT(s1, f1)  { Serial.print(s1); Serial.println(f1); }

#define streq(s1, s2)  (strcmp(s1,s2) == 0)


typedef struct {
  long z;
  //  char state;  // 0 - stopped, 1 accellerating, 2 steady speed, 3 decellerating
} t_pos;

#define S_STOP 0
#define S_ACC 1
#define S_STEADY 2
#define S_DEC 3

typedef enum move_calculation_type { movement_rotational_based, movement_time_based } move_calculation_type;

typedef struct {
  float rpm;
} t_rotation;

typedef struct {
  float feedMmPerRot; // mm / rev
  float feedMmPerMin; // mm / minute
  move_calculation_type current_move_type; // rotational based (mm/rot), or time based (mm/min)
} t_feed;

typedef struct {
  float pitch; // pitch of lead screw
  float stepsPerRev; // microsteps per revolution
  float stepsPerMM;  // steps per mm
} t_leadscrew;


extern char stepPin;
extern char dirPin;
extern char stepPinBit;
extern char dirPinBit;

extern char hallPin;

extern volatile t_pos pos;   // tool position
extern volatile t_rotation spindle; // spindle related stuff
extern t_feed z_feed; 
extern t_leadscrew z_screw; 

void SendUser(char *);
