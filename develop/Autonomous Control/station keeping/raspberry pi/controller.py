"""
Updated on FRI DEC 29 13:56:39 2018

@author: Zeyuan Feng

@contributor: fahah & Lianxin Zhang

*Get the command from sailboat object.
*Execute the command
*Update the global values
"""

import time
import os
import pigpio
import globalvar as gl
from sailboat_for_controller_v2 import sailboat
import math
os.system('sudo killall -9 pigpiod')
os.system('sudo pigpiod')
time.sleep(1)

#-------------Receiving Commands-----------------
def run():
    
    #-----------ESC Configuration----------------------
    
    ESC3 = 27 # Rudders
    ESC4 = 22 # Sails

    STBY = 23
    
    gl.set_value('x',0)
    gl.set_value('y',0)
    
    BUFFER_SIZE = 1024 # For TCP receiver
    #--------------------------------------------------
    
    gl.set_value('flag',False)
    angle = 1300 # Rudder Straight
    rudder=0
    sail=0

    
    pi = pigpio.pi()
    
    
    my_boat=sailboat()
    target=my_boat.target
    gl.set_value('target',target)
    times=0
    last_rudder_value=0
    last_sail_value=0
    while True:
        times=(times+1)%10
        
        if my_boat.flag==True:
            gl.set_value('flag',True)
            print('Program stops!')
            break

        ## change the frequency of communication when the sailboat arrives at its target area
        if my_boat.if_keeping==True:
            gl.set_value('frequency',20)
        else:
            gl.set_value('frequency',10)
        frequency=gl.get_value('frequency')
        
        ##get information of sailboat
        x=gl.get_value('x')
        y=gl.get_value('y')
        heading_angle=gl.get_value('heading_angle')
        my_boat.frequency=frequency
        my_boat.updata_pos(x,y,heading_angle)
        v=my_boat.velocity[0]
        u=my_boat.velocity[1]
        w=my_boat.angular_velocity
        
        ##control the rudder and sail
        rudder,sail,desired_angle=my_boat.update_state()
        rudder= float('{0:.1f}'.format(rudder))
        sail= float('{0:.1f}'.format(sail))
        rudder_output=1500-rudder*600
        sail_output=950+sail*612
        
        if sail_output>1750:
            sail_output=1750
        if sail_output<950:
            sail_output=950

        ## To prevent the high current leading to a breakdown, the rudder and sail are controlled saperately.
        if times%3 ==1:
            if last_rudder_value!=rudder:
                print('rudder',rudder)
                pi.set_servo_pulsewidth(ESC3,rudder_output)
        elif times%5 ==0: 
            if last_sail_value!=sail:
                print('sail',sail)
                pi.set_servo_pulsewidth(ESC4,sail_output) 
        
        last_rudder_value=rudder
        last_sail_value=sail

        #change the global variables
        gl.set_value('v',v)
        gl.set_value('u',u)
        gl.set_value('w',w)
        gl.set_value('rudder',rudder) # PWM for Motor1
        gl.set_value('sail',sail) # PWM for Motor2
        gl.set_value('desired_angle',desired_angle)

        time.sleep(1/frequency)
    
    # End the program        
    
    pi.set_servo_pulsewidth(ESC3,angle) # Rudder Straight
    pi.set_servo_pulsewidth(ESC4,900) # Sails Tighten
    print('Motors Stopped \n')
    time.sleep(0.4)
    pi.stop()
    time.sleep(0.5)

    

def control_angle(last_rudder,current_rudder):
    turning_time=abs(last_rudder-current_rudder)
    turning_direction=sign(current_rudder-last_rudder)
    output=1300+turning_direction*400
    return turning_time, output


def sign(x):
    if x>0:
        return 1
    elif x==0:
        return 0
    else:
        return -1

#    conn.close()
#    time.sleep(1)
#    print('Connection closed!')

#------------------------------------------------
