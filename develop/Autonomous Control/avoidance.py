
from pid import PID
import time 
import serial
import math
import pymysql
import threading
import re

ser=serial.Serial('COM5',57600)
"""create a pid control object"""
control=PID()

sailboat_angle=0
x=0
y=0
obstacle_y=0
obstacle_x=0
output=0
radius=30
angle1=0
angle2=0
setpoint=0

if_close=0
ini_angle=0
sail=55
turning_state=0
db = pymysql.connect("192.168.0.102","root","root","star")
cursor = db.cursor()

newPoint=0
xValue=0
yValue=0
#data=[0]*17



def abs_del_angle(angle_a,angle_b):
    if angle_a<0 and angle_b>angle_a+180:
        angle_b-=360
    elif angle_a>0 and angle_b<angle_a-180:
        angle_b+=360
    del_angle=abs(angle_a-angle_b)
    return del_angle
"""get the angle when the boat is automously sail in the pool"""
def get_setpoint2(xValue,yValue):
    global newPoint
    
    if xValue==yValue==0:
        newPoint=-160
    elif xValue==1 and yValue==1:
        newPoint=20
    elif xValue==1 and yValue==0:
        newPoint=-20
    elif xValue==0 and yValue==1:
        newPoint=160
    else: 
        newPoint=newPoint
    return newPoint

'''get sailboat angle by the displacement'''
# def get_angle1(del_x,del_y):
#     global angle1
#     if del_x !=0 and del_x**2+del_y**2>3:
#         angle1=int(math.atan(del_y/del_x)*57.32)
    
#         if del_x<0 and del_y<0:
#             angle1-=180
#         elif del_x<0 and del_y>=0:
#             angle1+=180
   
#         elif del_y>0:
#             angle1=90
#         else:
#             angle1=-90
#     else:
#         angle1=angle1
#     # print(' del_x:',del_x,' del_y:',del_y,end=' ')
#     print('angle1',angle1,end=' ')
#     return angle1


def get_angle2(del_x,del_y):
    global angle2
    if del_x !=0:
        angle2=int(math.atan(del_y/del_x)*57.32)
    # elif y>0:
    #     angle=90
    # else:
    #     angle=-90
        if del_x<0 and del_y<0:
            angle2-=180
        elif del_x<0 and del_y>0:
            angle2+=180
    # print('obs_angle',angle2,end=' ')
    # print(' del_x:',del_x,' del_y:',del_y,end=' ')
    return angle2



'''
##if the sailboat has turnned around the obstacle, it will leave.
## once the sailboat gets close to the obstacle, the function will get the initial angle.  After turning over 150 degrees, it will leave.'''
def if_leave(sailboat_angle,distance):
    global if_close,ini_angle,sail
    
    if if_close==0 and distance<80:
        ini_angle=sailboat_angle
        sail=35
        if_close=1
        
        
        # print('ini',ini_angle)
        
        return False
    elif if_close==1 and abs_del_angle(sailboat_angle,ini_angle)>130:
        
        if_close=0
        sail=55
        return True

"""get angle according to the tangent line"""
def get_setpoint(sailboat_angle,obstacle_angle,x,y,obstacle_x,obstacle_y):
    # if turning_state==0:
    if obstacle_angle<0 and sailboat_angle>obstacle_angle+180:
        sailboat_angle-=360
    elif obstacle_angle>0 and sailboat_angle<obstacle_angle-180:
        sailboat_angle+=360
    
    distance=math.sqrt((obstacle_x-x)**2+(obstacle_y-y)**2)
    # print('d ',distance,end=' ')
    if distance>radius:
        delta_angle=math.asin(radius/distance)*57.32
    else:
        if sailboat_angle>obstacle_angle:
            delta_angle=90
        else:
            delta_angle=-90
    # print('del' ,delta_angle)

    if sailboat_angle>obstacle_angle:
        SetPoint=obstacle_angle+delta_angle
        if if_close==1:
            SetPoint+=20
    else:
        SetPoint=obstacle_angle-delta_angle
        if if_close==1:
            SetPoint-=20
            

    '''After turning around the obstacle'''
    # else:
    #     if obstacle_angle<0:
    #         SetPoint=obstacle_angle+180
    #     else:
    #         SetPoint=obstacle_angle-180
    # print(delta_angle)
    return SetPoint

def reverse(newPoint):
    newPoint=newPoint+180
    if newPoint>180:
        newPoint-=360
    return newPoint
    
def send():
    global output
    last_send_time=time.time()
    while True:
        if time.time()-last_send_time>0.1:
            last_send_time=time.time()
            command=100*int(90+output*36/255)+sail
            command=(','+str(command)).encode(encoding='utf-8')
            ser.write(command)
    # print(85+output*36/255,end=' ')
    # print(85+output*36/255)

def update_value(x,y):
    global xValue,yValue
    if x<430:
        xValue=1
        
    elif x>740:
        xValue=0
        
    if y<400:
        yValue=1
        
    elif y>750:
        
        yValue=0

def read():
    global output,xValue,yValue,x,y,sail
    last_read_time=time.time()
    a=0
    while True:
        mess=0
        
        if time.time()-last_read_time>0.05:
            
            lastTime=time.time()
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

            if sailboat_angle<-180:
                sailboat_angle+=360
            if ser.inWaiting()>10:
                print('...')
                ser.flushInput()

            print('  sailboat angle',sailboat_angle)
          
            y=data[4]
            x=data[5]
            obstacle_y=data[15]
            obstacle_x=data[16]

            # sailboat_angle=get_angle1(x-last_x,y-last_y)
            obstacle_angle=get_angle2(obstacle_x-x,obstacle_y-y)
            newPoint=get_setpoint(sailboat_angle,obstacle_angle,x,y,obstacle_x,obstacle_y)

            distance=math.sqrt((x-obstacle_x)**2+(y-obstacle_y)**2)
            # print((x,y),end=' ')
            # print((obstacle_x,obstacle_y),end=' ')
            print('rudder:',85+output*36/255,end=' ')
            
            # if if_leave(sailboat_angle,distance):
            #     # newPoint=reverse(newPoint)
            #     obstacle_number+=1
            # print(newPoint)
            update_value(x,y)
            if newPoint>35 and newPoint<145 and turning_state==0
                newPoint=get_setpoint2(xValue,yValue)
            # print('setpoint',newPoint,end='')
            
            
            print(newPoint)
            # print(x,y,end=' ')
            # print(obstacle_x,obstacle_y)
            last_output=output
            if abs_del_angle(sailboat_angle,newPoint)>15:
                control.setPerameter(4,1,2)
                print('agg')
            else:
                control.setPerameter(1.5,4,0.5)
                print('cons')
            output=control.update(sailboat_angle,newPoint)
            
                
        # send(output,sail)
'''not tested'''
def read_data():
    global data
    last_data_time=time.time()
    while True:
        if time.time()-last_data_time>0.1:
            last_data_time=time.time()
            cursor.execute("SELECT * FROM data where Id=1")
            data = cursor.fetchone()


th_read=threading.Thread(target=read)
th_read.setDaemon(False)#守护线程  
th_read.start()
th_send=threading.Thread(target=send)
th_send.setDaemon(False)#守护线程  
th_send.start()
"""not tested"""
th_data=threading.Thread(target=read_data)
th_data.setDaemon(False)#守护线程  
th_data.start()






        
