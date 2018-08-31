from pid import PID
import time 
import serial
import math
import pymysql
from sailboat import sailboat
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import threading


control=PID()
sailboat=sailboat()
sailboat_angle=0
x=0
y=0
obstacle_y_list=[300,600,800,1000]
obstacle_x_list=[800,800,800,900]
output=0
radius=50
xValue=0
yValue=0
if_close=0
ini_angle=0
last_output=0


# ser=serial.Serial('COM5',57600)

'''
## if 45<angle<135,the sailboat will not going to trying to get close to the obstacle,but cruise in the whole area.
## every time touch the boundary, it will change another direction(20,-20,160,-160)'''

def update_value(x,y):
    global xValue,yValue
    if x<230:
        xValue=1
        
    elif x>840:
        xValue=0
        
    if y<320:
        yValue=1
        
    elif y>850:
        
        yValue=0
def get_setpoint2():
    global setpoint
    
    if xValue==yValue==0:
        setpoint=-160
    elif xValue==1 and yValue==1:
        setpoint=20
    elif xValue==1 and yValue==0:
        setpoint=-20
    elif xValue==0 and yValue==1:
        setpoint=160
    else: 
        setpoint=setpoint
    return setpoint

'''
##send command to the sailboat every 0.1 second.'''
def send():
    global output,last_output
    last_send_time=time.time()
    while True:
        if time.time()-last_send_time>0.1:
            last_send_time=time.time()
            command=100*int(85+output*36/255)+70
            command=(','+str(command)).encode(encoding='utf-8')
            print('command')
            # ser.write(command)
'''
##return the absolute value of the difference between two input angle'''
def abs_del_angle(angle_a,angle_b):
    if angle_a<0 and angle_b>angle_a+180:
        angle_b-=360
    elif angle_a>0 and angle_b<angle_a-180:
        angle_b+=360
    del_angle=abs(angle_a-angle_b)
    return del_angle



# def create_list():
#     global x_list,y_list,obstacle_y_list,obstacle_x_list,x,y
#     x_list=[]
#     y_list=[]
#     for i in range(0,100):
#         x_list.append(200)
#         y_list.append(300-3*i)
#     obstacle_x_list=obstacle_y_list=[150,300,500]
#     y=300
#     x=200



'''
##if the sailboat has turnned around the obstacle, it will leave.
## once the sailboat gets close to the obstacle, the function will get the initial angle.  After turning over 150 degrees, it will leave.'''


def if_leave(sailboat_angle,distance):
    global if_close,ini_angle
    
    if if_close==0 and distance<100:
        ini_angle=sailboat_angle
        if_close=1
        
        print('ini',ini_angle)
        
        return False
    elif if_close==1 and abs_del_angle(sailboat_angle,ini_angle)>150:
        if_close=0
        control.clear()
        return True

# def add_obstacle(obstacle_angle):
#     if obstacle_angle>45 and obstacle_angle<135:
#         print('..') 


# def get_angle1(del_x,del_y):
#     global angle1
#     if del_x !=0:
#         angle1=int(math.atan(del_y/del_x)*57.32)
    
#         if del_x<0 and del_y<0:
#             angle1-=180
#         elif del_x<0 and del_y>0:
#             angle1+=180
   
#     elif del_y>0:
#         angle1=90
#     else:
#         angle1=-90
#     # print(' del_x:',del_x,' del_y:',del_y,end=' ')
#     print('angle1',angle1,end=' ')
#     return angle1

def get_angle2(del_x,del_y):
    global angle2
    if del_x !=0:
        angle2=int(math.atan(del_y/del_x)*57.32)
    
        if del_x<0 and del_y<0:
            angle2-=180
        elif del_x<0 and del_y>0:
            angle2+=180
    elif del_y>0:
        angle2=90
    else:
        angle2=-90
    # print('angle2',angle2,end=' ')
    # print(' del_x:',del_x,' del_y:',del_y,end=' ')
    return angle2

## get the direction which is the tangent line of the circle whose center is the obstacle

def get_setpoint(sailboat_angle,obstacle_angle,distance):
    
    # to make sure the sailboat will turn to the better direction
    if obstacle_angle<0 and sailboat_angle>obstacle_angle+180:
        sailboat_angle-=360
    elif obstacle_angle>0 and sailboat_angle<obstacle_angle-180:
        sailboat_angle+=360
    
    if distance>radius:
        delta_angle=math.asin(radius/distance)*57.32

    ## in case of the sailboat is inside the circle
    # elif sailboat_angle>obstacle_angle:
    #     delta_angle=90
    else:
        delta_angle=90
        
    
    if sailboat_angle>obstacle_angle:
        SetPoint=obstacle_angle+delta_angle
    else:
        SetPoint=obstacle_angle-delta_angle
    # else:
    #     if obstacle_angle<0:
    #         SetPoint=obstacle_angle+180
    #     else:
    #         SetPoint=obstacle_angle-180
    # print(delta_angle)
    print(SetPoint,end='aaa')
    return SetPoint,sailboat_angle




def main():
    global newPoint,sailboat_angle,x,y,obstacle_y,obstacle_x,output,lastTime,last_output
    
    last_main_Time=0
    obstacle_number=0

    
    rudder=85
    sail=1
    a=0
    while True:
        mess=0
        if time.time()-last_main_Time>0.1:
            last_output=output
            last_main_Time=time.time()
            
            '''read the direction from serail'''

            # mess=ser.readline()
            # mess=bytes.decode(mess)
            # mess=str(mess)
            # if mess!= 0:
            #     a=mess.split('.')[0]
            # sailboat_angle=45-int(a)
            # if sailboat_angle<-180:
            #     sailboat_angle+=360

            # print('angle',sailboat_angle,end='')
        
            
            obstacle_y=obstacle_y_list[obstacle_number]
            obstacle_x=obstacle_x_list[obstacle_number]

            
            
            distance=math.sqrt((obstacle_x-x)**2+(obstacle_y-y)**2)
            
            # print('current',x,y,end=' ')
            sailboat_angle=sailboat.volocity[1]
            obstacle_angle=get_angle2(obstacle_x-x,obstacle_y-y)
            
     
                
                
                  
            newPoint,sailboat_angle=get_setpoint(sailboat_angle,obstacle_angle,distance)
            update_value(x,y)  
            if newPoint>45 and newPoint<135 and if_close==0:
                
                newPoint=get_setpoint2()
                print('sss',newPoint)

            output=control.update(sailboat_angle,newPoint)
            if if_leave(sailboat_angle,distance):
                try:
                    obstacle_number+=1
                    a=obstacle_x_list[obstacle_number]
                except:
                    obstacle_number-=1
                    output=-output  
                      
            rudder=85+output*36/255
            location,volocity=sailboat.predict(rudder,sail)
            
            x=location[0]
            y=location[1]

            v_x=volocity[0]*math.cos(volocity[1]/57.32)
            v_y=volocity[0]*math.sin(volocity[1]/57.32)
            
                
                # send(output)
            
        

            # print(location,output)
            print(location,' ',obstacle_number,volocity)
            # print(int(newPoint))
            
def plot():
    global x,y
    plt.close()  #clf() # 清图  cla() # 清坐标轴 close() # 关窗口
    fig=plt.figure()
    ax=fig.add_subplot(1,1,1)
    plt.plot(obstacle_x_list, obstacle_y_list, 'ro')
# plt.axis([0, 6, 0, 20])
    ax.axis("equal") #设置图像显示的时候XY轴比例
    plt.grid(True) #添加网格
    plt.ion()  #interactive mode on             
    while True:
        ax.scatter(x,y,c='b',marker='.')
        
        plt.pause(0.1)


#define 3 threadings for ploting,sending and reading respectively
th_plot=threading.Thread(target=plot)  
th_plot.setDaemon(False)#守护线程  
th_plot.start()
th_main=threading.Thread(target=main)  
th_main.setDaemon(False)#守护线程  
th_main.start()

# th_send=threading.Thread(target=send)  
# th_send.setDaemon(False)#守护线程  
# th_send.start()

            
