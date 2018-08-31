import pymysql
import time
import serial
import math
import threading
from pid import *
import re

xValue=1
yValue=1
if_evaluate=0
turning_state=0

control=PID()
sail=60
turning_state=0
output=0
setpoint=0

ser=serial.Serial('COM5',57600) 

db = pymysql.connect("192.168.0.102","root","root","star")
cursor = db.cursor()

data=[0]*6
x=0
y=0
def get_angle1(del_x,del_y):
    global angle1
    if del_x !=0:
        angle1=int(math.atan(del_y/del_x)*57.32)
    
        if del_x<0 and del_y<0:
            angle1-=180
        elif del_x<0 and del_y>0:
            angle1+=180
   
    elif del_y>0:
        angle1=90
    else:
        angle1=-90
    # print(' del_x:',del_x,' del_y:',del_y,end=' ')
    print('angle1',angle1,end=' ')
    return angle1

def abs_del_angle(angle_a,angle_b):
    if angle_a<0 and angle_b>angle_a+180:
        angle_b-=360
    elif angle_a>0 and angle_b<angle_a-180:
        angle_b+=360
    del_angle=abs(angle_a-angle_b)
    return del_angle

def if_turning(turning_state,sailboat_angle,setpoint):
    global sail
    
    # if turning_state==1:
    if abs_del_angle(sailboat_angle,setpoint)>30:
        
        # print('turning',end=' ')
        sail=35
    else:
        # print('finish turning',end=' ')
        get_setpoint()
        # turning_state=0 
        

def send():
    last_send_time=time.time()
    while True:
        
        if time.time()-last_send_time>0.1:
            last_send_time=time.time()
            command=100*int(90+output*33/255)+sail
            # print('rudder',90+output*33/255,end=' ')
            command=(','+str(command)).encode(encoding='utf-8')
            
            ser.write(command)


def get_setpoint():
    global setpoint,sail,turning_state
    
    control.clear()
    if xValue==yValue==0:
        setpoint=-160
        sail=40
    elif xValue==1 and yValue==1:
        setpoint=20
        sail=50
    elif xValue==1 and yValue==0:
        setpoint=-20
        sail=40
    elif xValue==0 and yValue==1:
        setpoint=160
        sail=50
    else: 
        setpoint=setpoint
    return setpoint


def read():
    global x,y,xValue,yValue,sailboat_angle,setpoint,sail,output,data
    a=0
    times=0
    last_read_time=time.time()
    
    while True:
        if time.time()-last_read_time>0.1:
            times+=1
            mess=0
            last_read_time=time.time()
            mess=ser.readline()
            mess=bytes.decode(mess)
            mess=str(mess)
            if mess!=0:
                print(mess)
                a=mess.split('.')[0]
                a=re.sub('\D','',a)
                try:    
                    b=int(a)
                except:
                    b=b
            ''' not tested'''
            # mess=re.sub('\D','',mess)
            # if re.match(r"(\d+)\.(\d+)", mess):
            #     b=int(mess)


            sailboat_angle=43-b
            '''b is from 0 to 360'''

            # print('rudder',rudder)
            if sailboat_angle<-180:
                sailboat_angle+=360
            if ser.inWaiting()>7:
                # print('...')
                ser.flushInput()
            
            
       
            if x<450:
                xValue=1
                
            elif x>800:
                xValue=0
                
            if y<200:
                yValue=1
                
            elif y>700:
                
                yValue=0
            setpoint=get_setpoint()
            if_turning(turning_state,sailboat_angle,setpoint)


            if abs_del_angle(sailboat_angle,setpoint)>15:
                control.setPerameter(4,1,2)
                # print('agg')
            else:
                control.setPerameter(1.5,4,0.5)
                # print('cons')

            
            print('sailboat angle',sailboat_angle,'setpoint',setpoint)
            output=control.update(sailboat_angle,setpoint)
        # send(output,sail)
def data():
    global data,x,y
    data_time=time.time()
    while True:
        if time.time()-data_time>0.1:
            data_time=time.time()
            cursor.execute("SELECT * FROM data where Id=1")
            data = cursor.fetchone()
            x=data[5]
            y=data[4]
# db.close()

th_read=threading.Thread(target=read)
th_read.setDaemon(False)#守护线程  
th_read.start()
th_send=threading.Thread(target=send)
th_send.setDaemon(False)#守护线程  
th_send.start()
th_data=threading.Thread(target=data)
th_data.setDaemon(False)#守护线程  
th_data.start()