int comInt;  
#include <Servo.h>
#include <Wire.h>
#include <JY901.h>
#include <Adafruit_INA219.h>

#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

Adafruit_INA219 ina219;

float shuntvoltage = 0;
float busvoltage = 0;
float current_mA = 0;
float loadvoltage = 0;
long time,lasttime;
int Ms=100;
Servo rudder;  // create servo object to control a servo
Servo sail;
int pos_rudder=90;
int pos_sail=115;

void move_rudder(){
  if(30<=pos_rudder && pos_rudder<=123){
    rudder.write(pos_rudder);
    
  }
}
void move_sail(){
  if(55<=pos_sail && pos_sail<=115){
    sail.write(pos_sail);
    
  }
}
void setup() {  
  
  rudder.attach(4);
  sail.attach(5);
  Serial.begin(57600);
  JY901.StartIIC(); 
  uint32_t currentFrequency;
  ina219.begin(); 
  while(Serial.read()>= 0){}//clear serialbuffer  
}  
void sendmess(){
  JY901.GetAngle();
//  Serial.print("Angle:");Serial.print((float)JY901.stcAngle.Angle[0]/32768*180);Serial.print(" ");Serial.print((float)JY901.stcAngle.Angle[1]/32768*180);Serial.print(" ");
  Serial.println((float)JY901.stcAngle.Angle[2]/32768*180);
//  shuntvoltage = ina219.getShuntVoltage_mV();
//  busvoltage = ina219.getBusVoltage_V();
//  current_mA = ina219.getCurrent_mA();
//  loadvoltage = busvoltage + (shuntvoltage / 1000);
////  
//  Serial.print(","); Serial.print(busvoltage); 
//  Serial.print(","); Serial.print(shuntvoltage);
//  Serial.print(","); Serial.print(loadvoltage);
//  Serial.print(","); Serial.println(current_mA); 
  }
void loop() { 
//  sendmess();
  
  
  time=millis();//去现在时间(ms)
  if(time-lasttime>=Ms){
    lasttime=time;
    sendmess();
    Serial.flush();
  }
 
  char command=Serial.read();
  if(command==byte(',')){   
      comInt = Serial.parseInt();     
      pos_rudder=comInt/100;
      pos_sail=comInt%100+25;
      move_rudder();
      move_sail();
    }  
  
    // clear serial buffer  

}  
