import pymysql
import time
import serial
import math
import threading

xValue=1
yValue=1
setpoint=0

# def send():
#     global setpoint
#     command=(',0').encode(encoding='utf-8')
#     if xValue==yValue==-1:
#         command=(',170').encode(encoding='utf-8')
#     elif xValue==1 and yValue==1:
#         command=(',0').encode(encoding='utf-8')
#     elif xValue==1 and yValue==-1:
#         command=(',110').encode(encoding='utf-8')
#     else:
#         command=(',-50').encode(encoding='utf-8')
#     ser_a.write(command)
#     ser_b.write(command)

# ser_a=serial.Serial('COM7',57600) 
# ser_b=serial.Serial('COM11',57600) 

db = pymysql.connect("192.168.0.101","root","root","star")
cursor = db.cursor()
cursor.execute("SELECT * FROM data where Id=1")
data = cursor.fetchone()

data=[0]*10
def controlFunction():
    global a_x
    global a_y
    global xValue
    global yValue
    global data
    lastTime=time.time()
    while True:
        if time.time()-lastTime>0.1:
            # lastTime=time.time()
            # mess=ser_a.readline()
            # mess=bytes.decode(mess)
            # mess=str(mess)
            # direction=mess.split(',')[0]
            # print(direction)
            # ser_a.flush()
            cursor.execute("SELECT * FROM data where Id=1")
            data = cursor.fetchone()
            
            a_x=data[4]
            a_y=data[5]
            print(a_x,a_y,end='')
            # if x<430:
            #     xValue=1
            #     send()
            # elif x>840:
            #     xValue=-1
            #     send()
            # if y<359:
            #     yValue=1
            #     send()
            # elif y>800:
            #     send()
            #     yValue=-1

def followFunction():
    global b_x
    global b_y
    lasttime=time.time()
    while True:
        if time.time()-lasttime>0.1:
            # lasttime=time.time()
            # mess=ser_b.readline()
            # mess=bytes.decode(mess)
            # mess=str(mess)
            # direction=mess.split(',')[0]
            # turningstate=mess.split(',')[1]
            # ser_b.flush()
            cursor.execute("SELECT * FROM data where Id=1")
            data2 = cursor.fetchone()
            a=data2
            b_x=a[8]
            b_y=a[9]
            print(b_x,b_y)
            # if turningstate =='1':
            #     if b_y-a_y<50:
            #         setpoint_adjust=-5*xValue
            #         setpoint_command=('p'+str(setpoint_adjust)).encode(encoding='utf-8')
            #         ser_b.write(setpoint_command)
            #     elif b_y-a_y>90:
            #         setpoint_adjust=5*xValue
            #         setpoint_command=('p'+str(setpoint_adjust)).encode(encoding='utf-8')
            #         ser_b.write(setpoint_command)
            #     if b_x-a_x>20:
            #         sail_adjust=-5*xValue
            #         sail_command=('s110').encode(encoding='utf-8')
            #         ser_b.write(sail_command)
            #     elif b_x-a_x<-20:
            #         sail_command=('s90').encode(encoding='utf-8')
            #         ser_b.write(sail_command)
a_control=threading.Thread(target=controlFunction)  
a_control.setDaemon(False)#守护线程  
a_control.start()
b_control=threading.Thread(target=followFunction)  
b_control.setDaemon(False)#守护线程  
b_control.start()  
db.close()
