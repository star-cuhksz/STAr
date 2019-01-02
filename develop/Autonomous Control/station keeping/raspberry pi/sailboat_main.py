"""
Created on FRI DEC 28 14:29:21 2018

@author: Zeyuan Feng

@contributor: fahah & Lianxin Zhang

Main program for station keeping. 
"""


import time
# import tcpserver
import globalvar as gl
import threading
import controller
# import RPi.GPIO as GPIO
import IMU
import sensor
import database
# import matplotlib.pyplot as plt


if __name__ == "__main__":
    
    gl.set_value('flag',False) # Stop sign
    gl.set_value('heading_angle',0) # initial heading angle zero
    gl.set_value('desired_angle',0)
    gl.set_value('sail',1300) 
    gl.set_value('rudder',1300)
    gl.set_value('frequency',10)
    # g1.set_value('target',[0,0]) 
    gl.set_value('x',0)
    gl.set_value('y',0)
    
    # conn = tcpserver.tcpserver()
    
    t1 = threading.Thread(target= controller.run) # Receiving Commands
    t2 = threading.Thread(target= IMU.IMU)
    t3 = threading.Thread(target= sensor.sensor)
    t4 = threading.Thread(target= database.run)
    

    t1.start() # start thread 1
    t2.start() # start thread 2
    t3.start() # start thread 3
    t4.start()
    
    t1.join() # wait for the t1 thread to complete
    t2.join() # wait for the t2 thread to complete
    t3.join() # wait for the t3 thread to complete
    t4.join()

    # conn.close()
    time.sleep(1)
    print('Connection closed!')
    
    
#-----------------------------------------------------------


# import time
# import threading
# import controller
# import IMU_for_sailboat
# import current_sensor
# import data_writer


# if __name__ == "__main__":
    
#     my_IMU=IMU_for_sailboat.IMU()
#     my_current_sensor=current_sensor.c_sensor()
#     my_controller=
#     my_writer=data_writer.d_writer('test1.xls')
    
#     t1 = threading.Thread(target= my_IMU.run_IMU) # Receiving Commands
#     t2 = threading.Thread(target= my_current_sensor.run)
#     t3 = threading.Thread(target= my_writer.run)
    

#     t1.start() # start thread 1
#     t2.start() # start thread 2
#     t3.start() # start thread 3

    
#     t1.join() # wait for the t1 thread to complete
#     t2.join() # wait for the t2 thread to complete
#     t3.join() # wait for the t3 thread to complete

    
#     time.sleep(1)
#     print('Connection closed!')



#     thread1 :get IMU
#     thread2 :get sensor
#     thread3 :controller
#     thread4 :writer