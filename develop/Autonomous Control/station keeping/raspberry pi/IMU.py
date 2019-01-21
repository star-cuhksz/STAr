# -*- coding: utf-8 -*-
"""
Created on Tue May 15 10:43:44 2018
When this program starts, the heading angle will be 0 degree. 
To solve, the noise of IMU.
@author: Feng Zeyuan
"""

import sys
import time
import logging
import math
import globalvar as gl
# import numpy as np
from Adafruit_BNO055 import BNO055


def IMU():
        # Raspberry Pi configuration with serial UART and RST connected to GPIO 7:
    bno = BNO055.BNO055(rst=7)
        
        # Enable verbose debug logging if -v is passed as a parameter.
    if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
        logging.basicConfig(level=logging.DEBUG)

        # Initialize the BNO055 and stop if something went wrong.
    if not bno.begin():
        raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
      
        # Print system status and self test result.
    status, self_test, error = bno.get_system_status()
    print('System status: {0}'.format(status))
    print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
        # Print out an error if system status is in error mode.
    if status == 0x01:
        print('System error: {0}'.format(error))
        print('See datasheet section 4.3.59 for the meaning.')

        # Print BNO055 software revision and other diagnostic data.
#        sw, bl, accel, mag, gyro = bno.get_revision()
#        print('Software version:   {0}'.format(sw))
#        print('Bootloader version: {0}'.format(bl))
#        print('Accelerometer ID:   0x{0:02X}'.format(accel))
#        print('Magnetometer ID:    0x{0:02X}'.format(mag))
#        print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))


    print('Reading BNO055 data, press Ctrl-C to quit...')
        # stime = np.array([])
        # sheading_angle = np.array([])
        #CalibData = bno.get_calibration()
    CalibData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 0, 0] #Sensor Calibration data
    bno.set_calibration(CalibData) # Sensor Calibration


        # Print system calibration status
    system, gyr, accellro, magno = bno.get_calibration_status()
#        print('System Calibration Status = ',int(system)) # 0 for no calibration, and 3 for maximum calibration
#        print('Gyro Calibration Status = ',int(gyr))
#        print('Accelerometer Calibration Status = ', int(accellro))
#        print('Magnetometer Calibration Status = ', int(magno))
    
    # input('press to begin calibration')
    system, gyr, accellro, magno = bno.get_calibration_status()
    print('System Calibration Status = ',int(system)) # 0 for no calibration, and 3 for maximum calibration
    print('Gyro Calibration Status = ',int(gyr))
    print('Accelerometer Calibration Status = ', int(accellro))
    print('Magnetometer Calibration Status = ', int(magno))
    time.sleep(2)
    ### set reference heading angle
    
    reference_heading, ref_roll, pitch = bno.read_euler()
    print('ref',reference_heading)
    try: 
        
        last_heading_angle=0
        last_roll=0
        IMU_times=0
        while True:
            IMU_times=(IMU_times+1)%10
            frequency=gl.get_value('frequency')
            
            if gl.get_value('flag'):
                #print('Breaking loop')
                # Break when flag = True
                break
            
                # Read the Euler angles for heading_angle, roll, pitch (all in degrees).
            heading_angle, roll, pitch = bno.read_euler()
            roll=regular_roll(roll,last_roll,ref_roll)
            heading_angle=regular_angle(heading_angle,last_heading_angle,reference_heading)
            heading_angle=-heading_angle
            # heading_angle=-heading_angle
                #gl.set_value('heading_angle',heading_angle) # Shared the heading_angle information
            gl.set_value('heading_angle',heading_angle)
            gl.set_value('roll',roll)
            last_heading_angle=heading_angle
            last_roll=roll
            if IMU_times==0:
                print('heading_angle = {0:0.2F}'.format(heading_angle),'roll = {0:0.2F}'.format(roll))
                
                
            time.sleep(1/frequency)
            

    except:
        print('An exception occured \n')

    print('IMU Loop Ended \n')

## the unit of angle will be rad and the value will be referred to the reference heading angle.
## Sometimes there is a noise (usually about 2000°), it will be ignored
def regular_angle(angle,last_angle,reference_heading):
    if angle < 0 or angle > 360:
        return -last_angle
    else:
        angle=(angle-reference_heading)/57.32
        if angle>math.pi:
            angle-=2*math.pi
        if angle<-math.pi:
            angle+=2*math.pi
        return angle
def regular_roll(angle,last_angle,ref_roll):
    if angle < -90 or angle > 90:
        return last_angle
    else:
        angle=(angle-ref_roll)/57.32
        # if angle>math.pi/2:
        #     angle-=math.pi
        # if angle<-math.pi/2:
        #     angle+=math.pi
        return angle
