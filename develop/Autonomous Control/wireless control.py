from tkinter import *
root=Tk()
import math
import time
import threading
import serial
ser=serial.Serial('COM5',57600) 

def send():
    command=(-11/15488*rudder*rudder-79/176*rudder+90)//1*100+90-sail**2-7*sail
    command=(',,'+str(command)).encode(encoding='utf-8')
    ser.write(command)


root.geometry('800x600+150+50')
root.title('GUI')


can=Canvas(root,width=800,height=600,bg='white')
can.pack()


photo = PhotoImage(file=r'C:\Users\surface\AppData\Local\Programs\Python\Python36-32\libs\liangjiaoqi.gif')#PhotoImagecan be used for GIF and PPM/PGM color bitmaps
can.create_image(517, 222, image = photo)


#can.create_arc(300,120,750,570,extent=180,style=ARC,fill='#476042') #for turning rudder
x=525
y=345-(220**2-(525-x)**2)**(1/2)
r=225
pointer=can.create_line(x,y,525,345,fill='red',arrow=FIRST,tags='point')


can.create_rectangle(50,50,200,520) #for turning sail
first_sail=can.create_rectangle(50,426,200,520,fill='white')
second_sail=can.create_rectangle(50,332,200,426,fill='white')
third_sail=can.create_rectangle(50,238,200,332,fill='white')
fourth_sail=can.create_rectangle(50,144,200,238,fill='white')
fifth_sail=can.create_rectangle(50,50,200,144,fill='white')

can.create_text(345, 390, text = "Angle:",font="Times 12 underline", tags="angle")
angle=can.create_rectangle(380,370,480,410)
angle_value=can.create_text(430,390,text = ".",fill="blue")

can.create_text(345, 510, text = "Load Vol",font="Times 12 underline", tags="loadVol")
loadVol=can.create_rectangle(380,490,480,530)
load_value=can.create_text(430,510,text = ".",fill="blue")

can.create_text(345, 450, text = "Bus Vol:",font="Times 12 underline", tags="busVol")
busVol=can.create_rectangle(380,430,480,470)
bus_value=can.create_text(430,450,text = "None",fill="blue")

can.create_text(550, 450, text = "Shunt Vol:",font="Times 12 underline", tags="shuntVol")
shuntVol=can.create_rectangle(580,430,680,470)
shunt_value=can.create_text(630,450,text = "None",fill="blue")

can.create_text(550, 510, text = "Current:",font="Times 12 underline", tags="current")
current=can.create_rectangle(580,490,680,530)
current_value=can.create_text(630,525,text = ".",fill="blue")

keyinfo=None
sail=0
rudder=0
i=1

class myThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        
        self.func = func
        self.args = args
        
        self.setDaemon(False)
        self.start()    # 在这里开始
        
    def run(self):
        self.func(*self.args)


def draw_sail(num):
    all_five_sail=[first_sail,second_sail,third_sail,fourth_sail,fifth_sail]
    for it in all_five_sail:
        can.itemconfig(it,fill='white')
    five=['red','orange','yellow','green','blue']
    for i in range(0,num):
        can.itemconfig(all_five_sail[i],fill=five[i])

def draw_rudder(num):  
    global x
    global y
    global pointer
    global can
    x= 525 + r * math.tan(math.pi/180*0.5*num)
    y= 345 - (220**2-(525-x)**2)**(1/2)
    can.coords(pointer,(x,y,525,345))

def callback_rudder():
    global keyinfo
    while True:
        if keyinfo=='ll':
            reset_rudder()
        elif keyinfo=='Right' or 'Left':
            rudderfunc()
            

def reset_rudder():
    global rudder
    global can
    global pointer
    global reset
    global keyinfo
    # while keyinfo!='11' and keyinfo!=None:
    if rudder>0:    
        rudder-=2
        send()
        draw_rudder(rudder)
        # print('',end='')
        time.sleep(0.01)
    elif rudder<0:    
        rudder+=2
        send()
        draw_rudder(rudder)
        # print('',end='')
        time.sleep(0.01)
    if rudder==0:
        keyinfo=None
def rudderfunc():
    global rudder
    global x
    global can
    global pointer
    global keyinfo
    time.sleep(0.01)
    if keyinfo == 'Right' and 310<x<740:
        rudder+=2
        send()
    elif keyinfo == 'Right' and rudder == -88:
        rudder+=2
        send()
    elif keyinfo == 'Left' and 310<x<740:
        rudder-=2
        send()
    elif keyinfo == 'Left' and rudder == 88:
        rudder-=2
        send()

    
    # print('',end='')
    draw_rudder(rudder)


def sail_up():

    global sail
    if sail<5:
        sail+=1
        draw_sail(sail)
        send()
k=1
def sail_down():
    
    global sail
    if sail!=0:
        sail-=1
        draw_sail(sail)
        send()


def callback_keyinfo(event):
    global keyinfo
    keyinfo=event.keysym

def callback_sail_up(event):
    global keyinfo
    th_sail_up=threading.Thread(target=sail_up)
    if keyinfo=='Left' or 'Right':
        th_rudder=threading.Thread(target=rudderfunc)  
        th_rudder.setDaemon(False)#守护线程  
        th_rudder.start()  
        th_sail_up.setDaemon(False)#守护线程 
    else: 
        th_sail_up.setDaemon(False)
    th_sail_up.start()
    
def callback_sail_down(event):
    
    th_sail_down=threading.Thread(target=sail_down)  
    if keyinfo=='Left' or 'Right':
        th_rudder=threading.Thread(target=rudderfunc)  
        th_rudder.setDaemon(False)#守护线程  
        th_rudder.start()  
        th_sail_down.setDaemon(False)#守护线程 
    else: 
        th_sail_down.setDaemon(False)
    th_sail_down.start()

def callback(event):
    th_reset=threading.Thread(target=callback_rudder)  
    th_reset.setDaemon(False)#守护线程  
    th_reset.start()
    th_current_angle=threading.Thread(target=current_angle)  
    th_current_angle.setDaemon(False)#守护线程  
    th_current_angle.start()

    

def current_angle():
    global a 
    global keyinfo
    global i
    global current_value
    global angle_value
    global k
    ser.flush()
    lastTime=time.time()
    while True:
        mess=0
        if time.time()-lastTime>0.3:
            mess=ser.readline()
            mess=bytes.decode(mess)
            mess=str(mess)
            if mess!= 0:
                a=mess.split(',')[0]
                b=mess.split(',')[1]
                c=mess.split(',')[2]
                d=mess.split(',')[3]
                e=mess.split(',')[4]
            can.itemconfig(current_value,text=str(e))
            can.itemconfig(angle_value,text=str(a))
            can.itemconfig(bus_value,text=str(b))
            can.itemconfig(shunt_value,text=str(c))
            can.itemconfig(load_value,text=str(d))
def keyinfo_reset(self):
    global keyinfo
    keyinfo='ll'

can.bind('<Key-Right>',callback_keyinfo)
can.bind('<Key-Left>',callback_keyinfo)
can.bind('<Key-w>',callback_sail_up)
can.bind('<Key-s>',callback_sail_down)

can.bind('<FocusIn>',callback)
can.bind('<KeyRelease-Right>',keyinfo_reset) #绑定键盘松开事件 回弹指针
can.bind('<KeyRelease-Left>',keyinfo_reset) #绑定键盘松开事件 回弹指针
can.focus_set()

root.mainloop()