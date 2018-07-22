from pid import PID
import time 
import serial
import math
import pymysql

# ser=serial.Serial('COM5',57600)
def create_list():
    global x_list,y_list,obstacle_y_list,obstacle_x_list,x,y
    x_list=[]
    y_list=[]
    for i in range(0,100):
        x_list.append(3*i)
        y_list.append(200)
    obstacle_x_list=obstacle_y_list=[150]*100
    y=200


times=0
newPoint=0
control=PID()
sailboat_angle=0
x=0
y=0
obstacle_y=0
obstacle_x=0
output=0
radius=50
lastTime=time.time()
angle1=0
angle2=0


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
    print('angle2',angle2,end=' ')
    # print(' del_x:',del_x,' del_y:',del_y,end=' ')
    return angle2


def get_setpoint(sailboat_angle,obstacle_angle):
    # if turning_state==0:
    if obstacle_angle<0 and sailboat_angle>obstacle_angle+180:
        sailboat_angle-=360
    elif obstacle_angle>0 and sailboat_angle<obstacle_angle-180:
        sailboat_angle+=360
    distance=math.sqrt((obstacle_x-x)**2+(obstacle_y-y)**2)
    if distance>radius:
        delta_angle=math.asin(radius/distance)*57.32
    elif sailboat_angle>obstacle_angle:
        delta_angle=90
    else:
        delta_angle=-90
        

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
    return SetPoint

def send(output):
    command=100*(85+output*36/255)+70
    command=(','+str(command)).encode(encoding='utf-8')
    # ser.write(command)
    # print(85+output*36/255,end=' ')
    # print(85+output*36/255)

# db = pymysql.connect("192.168.0.102","root","root","star")
# cursor = db.cursor()

def main():
    global times,newPoint,sailboat_angle,x,y,obstacle_y,obstacle_x,output
    create_list()

    while times<100:
        
            # times=(times+1)%3
            # mess=ser.readline()
            # mess=bytes.decode(mess)
            # sailboat_angle=250-float(mess)
            # print(mess)
            # ser.flush()
            # times=(times+1)%3
            
        times=times+1
        
        
            # control.setpoint(newPoint)
        last_x=x
        last_y=y
        
        
        # print(x,y,obstacle_x,obstacle_y,end=' ')
        print(85+output*36/255,end=' ')
        print(int(newPoint))
            
        lastTime=time.time()
        # cursor.execute("SELECT * FROM data where Id=1")
        # data = cursor.fetchone()
        
        y=y_list[times]
        x=x_list[times]
        obstacle_y=obstacle_y_list[times]
        obstacle_x=obstacle_x_list[times]
        print('last',last_x,last_y,end=' ')
        print('current',x,y,end=' ')
        sailboat_angle=get_angle1(x-last_x,y-last_y)
        obstacle_angle=get_angle2(obstacle_x-x,obstacle_y-y)


        
        
        newPoint=get_setpoint(sailboat_angle,obstacle_angle)
        # print(newPoint)
        # print(x,y,end=' ')
        # print(obstacle_x,obstacle_y)
        
        output=control.update(sailboat_angle,newPoint)
        send(output)
            

main()


            
