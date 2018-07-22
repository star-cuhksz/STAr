import pymysql
import time
import serial
import math
import threading

xValue=1
yValue=1

def send():
    command=(',110').encode(encoding='utf-8')
    if xValue==yValue==0:
        command=(',170').encode(encoding='utf-8')
    elif xValue==1 and yValue==1:
        command=(',0').encode(encoding='utf-8')
    elif xValue==1 and yValue==0:
        command=(',110').encode(encoding='utf-8')
    else:
        command=(',-50').encode(encoding='utf-8')
    ser.write(command)

ser=serial.Serial('COM7',57600) 

db = pymysql.connect("192.168.0.101","root","root","star")
cursor = db.cursor()


control=threading.Thread(target=controlFunction)  
control.setDaemon(False)#守护线程  
control.start()
def controlFunction():
    while True:
        if time.time()-lastTime>0.1:
            lastTime=time.time()
            mess=ser.readline()
            mess=bytes.decode(mess)
            mess=str(mess)
            print(mess)
            ser.flush()
            cursor.execute("SELECT * FROM data where Id=1")
            data = cursor.fetchone()
            
            x=data[4]
            y=data[5]
            print(x,y)
            if x<430:
                xValue=1
                send()
            elif x>840:
                xValue=0
                send()
            if y<320:
                yValue=1
                send()
            elif y>850:
                send()
                yValue=0
    
    
db.close()