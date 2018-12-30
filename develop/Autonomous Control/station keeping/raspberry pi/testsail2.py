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
for i in range(33):
    # if i%10==0:
    #     pi.set_servo_pulsewidth(ESC3,1900)
    # elif i%10==1:
    #     pi.set_servo_pulsewidth(ESC3,1650)

    # elif i%10==5:
    #     pi.set_servo_pulsewidth(ESC3,1100)
    # else:
    #     pi.set_servo_pulsewidth(ESC3,1500)
    i=i%11
    pi.set_servo_pulsewidth(ESC4,1700)
    time.sleep(1.5)

# while True:
    
#     direction=input('please input direction')
    
#     run_time=float(input('please input time'))
#     d=0
#     if direction== 'a':
#         dc=0
#         d=-1
#     elif direction== 'c':
#         dc=55
#         d=1
#     elif direction== 'q':
#         break
#     output=1250+d*400
#     output=int(input('please input pwm'))
#     output2=int(input('please input pwm2'))
#     # p = gpio.PWM(pin, 725) # channel, frequency    # when dc=50, freq = 725 anticlockwise and freq=726 clockwise
    
#     #

#     # pi.set_servo_pulsewidth(ESC3,rudder_output)
#     pi.set_servo_pulsewidth(ESC4,output)
#     time.sleep(run_time)
#     pi.set_servo_pulsewidth(ESC4,output2)
#     time.sleep(run_time)
#     pi.set_servo_pulsewidth(ESC4,1250)
#     # p = gpio.PWM(pin, 900)
# #a = input('please type any key. ')

# p.stop()
# gpio.cleanup()