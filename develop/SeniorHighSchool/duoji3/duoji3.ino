 #include <Servo.h>
#include <Wire.h>
#include <JY901.h>
#include <Adafruit_INA219.h>

Servo myservo;  // create servo object to control a servo
Servo fan;
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position
int pos_fan = 0;
int posRudderPrint=0;
int number;
float angleacc = 0;
const int mind = 40;
const int maxd = 110;
 int servoStart = 74;
const float threshold = 0.005;
const float leastDelay = 1.5;
float dir = 0;
Adafruit_INA219 sensor;
void setup() {
  Serial.begin(57600);
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  fan.attach(10);
  pos = 90;
  pos_fan = 90;
  myservo.write(servoStart);
  fan.write(90);
  sensor.begin();
  JY901.StartIIC();
  resetServo ();
}

void getSensor(){
  float voltage = 0;
  float current = 0; // 以毫安为单位
  float power = 0;
  voltage = sensor.getBusVoltage_V();  //获取电压值
  current = sensor.getCurrent_mA();    // 获取电流值
  power = voltage * (current/1000); 
  Serial.print(" Voltage ");
  Serial.print(voltage); 
  Serial.print(" V ");  
  Serial.print(" Current: "); 
  Serial.print(current);
  Serial.print(" mA ");
  //Serial.print(" Power: "); 
  //Serial.print(power); 
  //Serial.println(" W ");  
}

void resetServo(){
  float dtime = 0;
  dtime = (100-abs(pos-80))*threshold+leastDelay;
  //Serial.println(dtime);
  delay(dtime*1000);
  if(dir <= -137 && dir >= -180){
    servoStart = 75;
  }
  if (dir <= 180 && dir >= 126){
    servoStart = 84;
  }
  pos = servoStart;
  posRudderPrint=servoStart;
  myservo.write(pos);
}

void loop() {
    JY901.GetAngle();
    JY901.GetAcc();
    Serial.print("Heading: ");
    Serial.print((float)JY901.stcAngle.Angle[2]/32768*180);
    dir = (float)JY901.stcAngle.Angle[2]/32768*180;
    char putout;
    putout=Serial.read();
    angleacc = JY901.stcAcc.a[2]/32768*16; 
    if(putout=='Z'){
       pos=Serial.parseInt();
       posRudderPrint=pos;
       if (pos >= mind && pos <= maxd){
          myservo.write(pos);
          resetServo();
       }
    }
    if(putout == 'F'){
       pos_fan=Serial.parseInt();
       if (pos_fan >= 50 && pos_fan <= 120){
        fan.write(pos_fan);
       }
    }
    getSensor();
    Serial.print (" Acceleration: ");
    Serial.print(angleacc);
    Serial.print(" RudderCommand: ");
    Serial.print(posRudderPrint);
    Serial.print(" SailCommand: ");
    Serial.println(pos_fan);
    delay(100); 
}
