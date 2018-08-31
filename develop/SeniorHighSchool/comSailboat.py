import pymysql
import time
import serial
import math
import threading
import datetime

#global command=''
db=pymysql.connect("192.168.0.102","root","root","star")



#f=open('record.txt', 'a')
 
ser=serial.Serial("COM4", 57600)
getSensor="start"
getCommand="starT"
def send():
	while True:
		global getCommand
		getCommand=input()
		command=getCommand.encode(encoding='utf-8')
		ser.write(command)
		print('test')
		#f.write("test sentence")
		time.sleep(0.1)
	#command=('R110B').encode(encoding='utf-8')

	
def read():
	while True:
		#database
		cursor = db.cursor()
		cursor.execute("SELECT * FROM data WHERE id=1")
		dataSTAr = cursor.fetchone()
		xPosition=dataSTAr[4]
		yPosition=dataSTAr[5]
		#Sensor
		global getSensor
		line = ser.readline()
		if line:
			result = line.strip().decode()
			getSensor=result
			timeFlag=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			with open('record.txt', 'a') as f:
				f.write(str(timeFlag)+" "+str(getCommand))
				f.write(" xPosition: "+str(xPosition)+" yPosition: "+str(yPosition))
				f.write(" "+str(getSensor)+" EOF")
				f.write("\n")
			getSensor="sensor"
			#print(getSensor)
			print(result)
		time.sleep(0.1)

"""
def controlFunction():
	While True:
		cursor.excute("SELECT * FROM data where Id=1")
		data=cursor.fetchone()
		x=data[4]
		y=data[5]
		print(x,y)

"""


t1=threading.Thread(target=send)
t2=threading.Thread(target=read)
t1.setDaemon(False)
t2.setDaemon(False)
t1.start()
t2.start()
#f.close()

	
#db.close()
  
