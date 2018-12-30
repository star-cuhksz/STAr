# -*- coding: utf-8 -*-
"""
Created on Tue May 15 11:05:38 2018

@author: CUHKSZ
"""

import time
import xlsxwriter
import random
from collections import deque
import globalvar as gl
from ina219 import INA219
from ina219 import DeviceRangeError



def sensor():
    
    global heading_angle
    global rudder
    global sail

    Shunt_OHMS = 0.1 # For this sensor it is 0.1 ohm
    
    try:
        print('Starting Current Sensor')
        print('Collecting Sensor Values...')
        start = time.time() # Start Time
        
        #global DataPoints
        DataPoints = deque(maxlen=None) # Creating Array of datatype Deque to store values

        a = 0.9664 # Regression Fitting Parameter
        b = 0.0285 # Regression Fitting Parameter

        ina = INA219(Shunt_OHMS) # Auto Gain
            
        ina.configure()
        print('Current Sensor Configured Successfully')
        while True:            
            frequency=gl.get_value('frequency')
            if gl.get_value('flag'):
                #print('Breaking loop')
                # Break when flag = True
                break
            
            
            #print('Bus Voltage: %.3f V' % ina.voltage())

            try:
                #print('Bus Current: %.3f mA' % ina.current())
                #print('Power: %.3f mW' % ina.power())
                ruddervalue= float('{0:.2f}'.format(gl.get_value('rudder')))
                sailvalue= float('{0:.2f}'.format(gl.get_value('sail')))
                currentvalue = round((a*ina.current())+b) # Rounding off values to nearest integer
                voltagevalue = float('{0:.1f}'.format(ina.voltage())) # Floating point up to one decimal point
                powervalue = round(currentvalue*voltagevalue)
                timevalue = float('{0:.1f}'.format(time.time()-start)) # Elapsed time in Seconds with 1 decimal point floating number 
                headingvalue = float('{0:.2f}'.format(gl.get_value('heading_angle')))
                DataPoints.append([timevalue, ruddervalue, sailvalue, gl.get_value('x'),gl.get_value('y'),gl.get_value('desired_angle'), headingvalue,currentvalue, voltagevalue, powervalue,gl.get_value('v'),gl.get_value('u'),gl.get_value('w')]) # Updating DataPoints Array
                print('current:',currentvalue,'voltage',voltagevalue)
            except DeviceRangeError:
                print('Device Range Error')

            time.sleep(1/frequency) # Reading value after 0.5 second
        
    except:        
        print('Exception Occurred, Current Sensor Stopped \n')

    
    Wt = input('Do you want to store the sensor values Y/N? ')

    if Wt == 'Y':
        writing(DataPoints)
    else:
        print('Ending without saving sensor data \n')

    print('Sensor Stopped!\n')
#------------------------------------------------

def writing(Data):
    file_name=input('please input the name')
    target='target:[3,6]'
    
    runDate = time.ctime() 
    workbook = xlsxwriter.Workbook('%s.xlsx'%file_name,{'constant_memory': True})  # Creating XLSX File for Data Keeping 
    worksheet = workbook.add_worksheet() # Generating worksheet

    bold = workbook.add_format({'bold':True}) # Formating for Bold text

    worksheet.write('A1', 'Time', bold) # Writing Column Titles
    worksheet.write('B1', 'rudder', bold)
    worksheet.write('C1', 'sail', bold)
    worksheet.write('D1', 'x', bold)
    worksheet.write('E1', 'y', bold)
    worksheet.write('F1', 'desired angle', bold)
    worksheet.write('G1', 'Heading Angle', bold)
    worksheet.write('H1', 'Current (mA)', bold)
    worksheet.write('I1', 'Voltage (v)', bold)
    worksheet.write('J1', 'Power (mW)', bold)
    worksheet.write('L1', 'v', bold)
    worksheet.write('M1', 'u', bold)
    worksheet.write('N1', 'w', bold)
    worksheet.write('K1', 'Start Time', bold)
    worksheet.write('K2', runDate)
    worksheet.write('K3', target)
    worksheet.write('K4', 'dM:1.8,dT:1')
    

    row = 1 # Starting Row (0 indexed)
    col = 0 # Starting Column (0 indexed) 
    

    n = len(Data) # Total number of rows
    print('Total number of rows: ',n)

    print('Writing Data into Worksheet')
        
    for Time, value1, value2, value3, value4, value5, value6, value7, value8, value9, value10, value11, value12 in (Data):
        # Writing Data in XLSX file
            
        worksheet.write(row, col, Time)
        worksheet.write(row, col+1, value1)
        worksheet.write(row, col+2, value2)
        worksheet.write(row, col+3, value3)
        worksheet.write(row, col+4, value4)
        worksheet.write(row, col+5, value5)
        worksheet.write(row, col+6, value6)
        worksheet.write(row, col+7, value7)
        worksheet.write(row, col+8, value8)
        worksheet.write(row, col+9, value9)
        worksheet.write(row, col+11, value10)
        worksheet.write(row, col+12, value11)
        worksheet.write(row, col+13, value12)
        row += 1

    
    workbook.close() # Closing Workbook 
    time.sleep(1)
    print('Sensor Writing successfull \n')
    
#-------------------------------------------------
# sensor()