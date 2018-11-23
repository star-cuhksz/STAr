/********************************************************
 * PID Adaptive Tuning Example
 * One of the benefits of the PID library is that you can
 * change the tuning parameters at any time.  this can be
 * helpful if we want the controller to be agressive at some
 * times, and conservative at others.   in the example below
 * we set the controller to use Conservative Tuning Parameters
 * when we're near setpoint and more agressive Tuning
 * Parameters when we're farther away.
 ********************************************************/
int comInt;  
#include <Servo.h>
#include <PID_v1.h>
#include <JY901.h>
#include <Adafruit_INA219.h>
//
Adafruit_INA219 ina219;

float shuntvoltage = 0;
float busvoltage = 0;
float current_mA = 0; 
float loadvoltage = 0;
//these variables are for current sensor


Servo rudder;  // create servo object to control a servo
Servo sail;
int pos_rudder=90;
int pos_sail=115;
long time,lasttime;
//Define Variables we'll be connecting to
double Setpoint, Input, Output,ini_Input;
int Ms=100;
int turningState=0;
float integral=0;
//Define the aggressive and conservative Tuning Parameters
//double aggKp=4, aggKi=0.2, aggKd=1;
//double consKp=1, consKi=0.05, consKd=0.25;
double aggKp=4, aggKi=0.2, aggKd=1;
double consKp=1, consKi=1.5, consKd=0.25;
int ref_angle=0;

//Specify the links and initial tuning parameters
PID myPID(&Input, &Output, &Setpoint, consKp, consKi, consKd, DIRECT);


void set_zero_angle(){
  JY901.GetAngle();
  ref_angle = (float)JY901.stcAngle.Angle[2]/32768*180;
}


void move_rudder(){
  if(45<=pos_rudder && pos_rudder<=123){
    rudder.write(pos_rudder);
    delay(10);
  }
}
void move_sail(){
  if(55<=pos_sail && pos_sail<=115){
    sail.write(pos_sail);
    
  }
}
void access_message(){
  char command=Serial.read();
  if(command==byte(',')){   
      Setpoint = Serial.parseInt();
      pos_sail=60;
      move_sail();
      turningState=0;
      myPID.SetNewPoint();
      consKi=consKi+integral*0.001;
      Serial.println(consKi);
      integral=0;
  }
  else if(command==byte('.')){   
    comInt = Serial.parseInt();     
    pos_sail=comInt;
    move_sail();
  }
  else if(command==byte('r')){
    set_zero_angle();
  }
}

void get_voltage(){
  shuntvoltage = ina219.getShuntVoltage_mV();
  busvoltage = ina219.getBusVoltage_V();
  current_mA = ina219.getCurrent_mA();
  loadvoltage = busvoltage + (shuntvoltage / 1000);
//  
  Serial.print(","); Serial.print(busvoltage); 
  Serial.print(","); Serial.print(shuntvoltage);
  Serial.print(","); Serial.print(loadvoltage);
  Serial.print(","); Serial.println(current_mA);
}

void get_del_angle(){
  ini_Input = (float)JY901.stcAngle.Angle[2]/32768*180-ref_angle;
    
  double gap = abs(Setpoint-ini_Input); //distance away from setpoint
  if (abs(ini_Input-Setpoint)<20)
  {  //we're close to setpoint, use conservative tuning parameters
    if(turningState == 0){
    turningState=1;
    pos_sail=110;
    move_sail();}
    else{
      integral+=(Setpoint-ini_Input)*0.1;
      }
  }
  if (gap < 20)
  {  //we're close to setpoint, use conservative tuning parameters
    myPID.SetTunings(consKp, consKi, consKd);
  }
  else
  {
     //we're far from setpoint, use aggressive tuning parameters
     myPID.SetTunings(aggKp, aggKi, aggKd);
  }
  // To garentee the boat to turn correctly in the following two situation
  if(Setpoint>0 && ini_Input<Setpoint-180){
    Input=360+ini_Input;
  }
  else if(Setpoint<0 && ini_Input>Setpoint+180){
    Input=ini_Input-360;
  }
  else{
    Input=ini_Input;
  }
}


void setup()
{
  rudder.attach(4);
  sail.attach(5);
  Serial.begin(57600);
  JY901.StartIIC();  
  while(Serial.read()>= 0){}//clear serialbuffer  
  
  //initialize the variables we're linked to
  lasttime=millis();
  Setpoint = 55;

  
//  uint32_t currentFrequency;
//  ina219.begin(); 
  //turn the PID on
  myPID.SetMode(AUTOMATIC);
  myPID.SetOutputLimits(-255, 255);
}

void loop()
{
  time=millis();//去现在时间(ms)
  if(time-lasttime>=Ms){
    lasttime=time;
    access_message();
    JY901.GetAngle();
    get_del_angle();
    myPID.Compute();//the output value will be rewrite here
    pos_rudder=84+Output*36/255;
    move_rudder();
    //get_voltage();

    Serial.println(ini_Input);
//Serial.print('b');Serial.print(pos_rudder);Serial.print('b');Serial.println(Output);
  }

}
