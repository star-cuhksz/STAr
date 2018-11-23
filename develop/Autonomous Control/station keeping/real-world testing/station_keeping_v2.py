from sailboat_v4_for_sk_v2 import sailboat
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import serial
import pymysql
import threading
import re
def sign(p):
    if p>0:
        return 1
    elif p==0:
        return 0
    else:
        return -1
x=0
y=0
start_time=time.time()
my_boat=sailboat()
ser=serial.Serial('COM5',57600) 

db = pymysql.connect("192.168.0.104","root","root","star")
cursor = db.cursor()

def send():
    global x,y
    last_send_time=time.time()
    while True:
        
        if time.time()-last_send_time>0.1:
            
            rudder=90-sign(my_boat.rudder)*pow(my_boat.rudder*57.32,2)/65
            sail=-my_boat.sail*57.32*1.4+91
            last_send_time=time.time()
            command=100*int(rudder)+sail
            print(rudder,sail,command)
            # print('rudder',90+output*33/255,end=' ')
            command=(','+str(command)).encode(encoding='utf-8')
            
            ser.write(command)
def read():
    global heading_angle
    
    last_read_time=time.time()
    b=0
    while True:
        if time.time()-last_read_time>0.1:
            
            mess=0
            last_read_time=time.time()
            mess=ser.readline()
            mess=bytes.decode(mess)
            mess=str(mess)
            if mess!=0:
                print(mess)
                a=mess.split('\n')[0]
                a=re.sub('\D','',a)

                
                try:    
                    b=int(a)
                except:
                    b=b
            # ser.flushInput()
        # print(b)
        heading_angle=b/57.32
    
        
        my_boat.heading_angle=heading_angle

def get_info():
    last_info_time=time.time()
    global x,y,rudder,sail,heading_angle
    while True:
        if time.time()-last_info_time>0.1:
            last_info_time=time.time()
            cursor.execute("SELECT * FROM data8802 where Id=1")
            data = cursor.fetchone()
            x=-data[2]/1000+3
            y=6-data[3]/1000
            my_boat.location[0]=x
            my_boat.location[1]=y
            
            if x<0.8:
                my_boat.x_value=1
            
            elif x>5:
                my_boat.x_value=-1
            if y<2:
                my_boat.y_value=1
            
            elif y>7:
                my_boat.y_value=-1
            my_boat.to_next_moment()
            print('x,y',[x,y],'heading,disired',[my_boat.heading_angle,my_boat.desired_angle],my_boat.x_value,my_boat.y_value)
            # info=my_boat.to_next_moment(x,y,heading_angle)
            # x=info[0][0]
            # y=info[0][1]
            # rudder=info[1]
            # sail=info[2]
            # # print(x,y,sail)
            # desired_angle=info[3]
            # heading_angle=info[4]
        # if time.time()-start_time>12:
        #     break
            # print('rudder',rudder,'sail',sail,'goal',desired_angle,'heading',heading_angle)


def plot():
    global x,y
    plt.close()  #clf() # 清图  cla() # 清坐标轴 close() # 关窗口
    fig=plt.figure()
    ax=fig.add_subplot(1,1,1)
    # plt.plot(obstacle_x_list, obstacle_y_list, 'ro')
# plt.axis([0, 6, 0, 20])
    ax.axis("equal") #设置图像显示的时候XY轴比例
    plt.grid(True) #添加网格
    plt.ion()  #interactive mode on             
    while True:
        ax.scatter(x,y,c='b',marker='.')
        
        plt.pause(0.1)

th_plot=threading.Thread(target=plot)  
th_plot.setDaemon(False)#守护线程  
th_plot.start()
th_main=threading.Thread(target=get_info)  
th_main.setDaemon(False)#守护线程  
th_main.start()
th_send=threading.Thread(target=send)
th_send.setDaemon(False)#守护线程  
th_send.start()
th_read=threading.Thread(target=read)
th_read.setDaemon(False)#守护线程  
th_read.start()