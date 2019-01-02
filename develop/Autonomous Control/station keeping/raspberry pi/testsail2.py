"""
Updated on Wed JAN 2 11:05:41 2019

@author: Zeyuan Feng

@contributor: fahah & Lianxin Zhang

You can use it to loose sail (PWM1750) before mounting the lid.
"""
import os
import pigpio
import RPi.GPIO as gpio
import time, sys




        
os.system('sudo killall -9 pigpiod')
os.system('sudo pigpiod')


ESC3 = 27 # Rudders
ESC4 = 22 # Sails

    
pi = pigpio.pi()
# pi.set_mode(STBY, pigpio.OUTPUT) # Setting GPIO 23 as OUTPUT

# pi.write(STBY,1) # Turining GPIO 23 High
 

pin = 22 # 4, 17, 27 rudder, 22  sail
dc =  55 # 0 ~ 50  anticlockwise, 55~99clockwise
#servo = 4

# gpio.setmode(gpio.BCM)
# gpio.setwarnings(False)
# gpio.setup(pin,gpio.OUT,initial=False)


    
# p = gpio.PWM(pin, 900) # channel, frequency    # when dc=50, freq = 725 anticlockwise and freq=726 clockwise
# p.start(0)

#pi = pigpio.pi()
#pi.set_servo_pulsewidth(servo,1500) #900~1700,  900 loosen, 1700 tighten
while True:
    a=input('input PWM')
    if a =='q':
        break
    try:
        a=int(a)
        if 950<=a and a<=1750:
            pi.set_servo_pulsewidth(ESC4,1750)
            time.sleep(0.5)
            print('Done')
        else:
            print('950<PWM<1750')
    except:
        print('PWM should be an integer')
    
    
print('program stops')
