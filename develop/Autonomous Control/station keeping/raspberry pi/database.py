"""
Created on Fri DEC 29 13:37:45 2018

@author: Zeyuan Feng

Read data from database
"""
import pymysql
import time
import re
import globalvar as gl
# import globalvar as gl
def run():
    

    db = pymysql.connect("192.168.0.104","root","root","star")
    cursor = db.cursor()
    while True:
        frequency=gl.get_value('frequency')
        if gl.get_value('flag'):
                #print('Breaking loop')
                # Break when flag = True
            break
        
        cursor.execute("SELECT * FROM data8802 where Id=1")
        data = cursor.fetchone()
        x=-data[2]/1000+3
        x=float('{0:.2f}'.format(x))
        y=6-data[3]/1000
        y=float('{0:.2f}'.format(y))
        # print(x,y)
        gl.set_value('x',x)
        gl.set_value('y',y)
        
        time.sleep(1/frequency)
# run()