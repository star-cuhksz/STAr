'''
Updated on Tue JAN 2 14:41:22 2019

@author: Zeyuan Feng


The angle is the same as a typical polar coordinate. The positive direction of axis is 0. The range is [0,2*pi] 
To use this program, you should import the code and create a sailboat object.
Firstly, call the method update_pos(), then update_state() to get new sail and rudder commands.
'''


import math
import random
import time
from pid2 import PID


class sailboat:


    def __init__(self,velocity=[0,0],heading_angle=0,course_angle=0,desired_angle=0,angular_velocity=0,location=[2,3],
    rudder=0,sail=0,sample_time=0.1,target=[3,6],IMU_sample_time=0.1,data_base_sample_time=0.1):
    ####    all the units of angles are rad 
        self.velocity=velocity ###[v,u], where v is the heading angle of the sailboat 
        self.heading_angle=heading_angle
        self.next_desired_angle=0
        self.desired_angle=desired_angle    
        self.angular_velocity=angular_velocity   ## w
        self.location=location   ###[x,y]
        self.rudder=rudder       ### the positive angle is corresponding to counterclockwise
        self.sail=sail           ### the positive angle is corresponding to counterclockwise
        self.last_v=0
        self.roll=0
        self.roll_angular_velocity=0

        self.target=target    ###the center of target area[x,y]   self.dM=10,which is the radius of the pre-arrived area ,self.dT=5,which is r of target area          
        self.frequency=10
        self.dT=1.4       ## radius of target area
        self.dM=2.8        ## radius of pre arrive
        self.desired_v=0
        self.maxrudder=math.pi/4  ##max angle of rudder
        self.maxsail=math.pi/12*5
        
        self.true_wind=[3,math.pi*3/2]       ##[wind speed, direction]
        self.app_wind=[3,math.pi*3/2]                  ##[wind speed, direction]
    
                      ###need to be adjusted ###
        self.tacking_sign=0
        self.tacking_velocity=0.5
        self.find_sail_sign=1
        self.optimal_sail_adjustment=0
        
        self.p1=0        ##drift coefficient####relative big for the plastic sailboat
        self.p2=4         ##tangential friction
        self.p3=2.5        ##angular friction
        self.p4=1.8         ##sail lift
        self.p5=30        ##rudder lift
        self.p6=0.05         ##distance to sail
        self.p7=0.05         ##distance to mast
        self.p8=0.25           ##distance to rudder
        self.p9=3         ##mass of boat
        self.p10=0.3        ##moment of inertia
        self.p11=0.3  
        self.p12=0.002   #wind effect on w   
        self.p13=0.045 #wind effect on v
        self.time=0

        self.rudder_controller=PID()

        self.d=3.65
        
        #this part is to add the boundary
        

        self.flag=False

        self.if_keeping=False
        self.keeping_state=1  ##1: before turning 2: turning 3:recover 4:go back
        self.start_tacking_time=-1
        self.init_tacking_sign=0

        self.v_list=[0]*5
        self.u_list=[0]*5
        self.w_list=[0]*5
        self.p_list=[0]*5
        
        self.tacking_state='not tacking'
        self.if_force_turning=False
        self.tacking_angle=0
        self.go_to_center_start_time=0
        self.go_to_center_angle=0.5
        
        self.sleep_time=0
    ## predict the state for next moment and make decision  
    def update_state(self):
        global n
        self.time+=1
        if self.time>3100:
            self.flag=True  #Stop the program
        
        if self.sleeper() != True:
            self.regular_all_angle()
            self.rudder_control()    
            
            self.sail_control()
            # self.sail,self.rudder=0,0
            self.get_desired_angle(self.target[0],self.target[1])

        if self.time>2800:  ### it's time to go home
            self.next_desired_angle=-math.pi/2
        # else:
        #     print('sleep',self.rudder)
        # self.desired_angle=0.7
        # self.rudder=0
        
        # if self.time%10==0:
        #     # print('rudder',self.rudder,'sail',self.sail,'desired_angle',self.desired_angle)
        #     # print('next angle',self.next_desired_angle)
        #     # print('keeping state',self.keeping_state,'d',self.d)
            # print('adjust sail by',self.optimal_sail_adjustment)
            # print(self.last_v,self.velocity[0])
        return self.rudder,self.sail,self.desired_angle

    def sleeper(self):
        if self.sleep_time>0:
            self.sleep_time-=1
            return True
        else:
            return False

    def regular_all_angle(self):
        self.heading_angle=self.regular_angle(self.heading_angle)
        self.desired_angle=self.regular_angle(self.desired_angle)
        self.roll=self.regular_angle(self.roll)

    def rudder_control(self):
        self.get_app_wind()
        self.app_wind[1]=self.regular_angle(self.app_wind[1])
        
        if self.keeping_state!=2 and self.keeping_state!=5:  
            self.heading_angle=self.regular_angle(self.heading_angle)
            
            self.desired_angle=self.regular_angle(self.desired_angle)
            if math.cos(self.heading_angle-self.desired_angle)>0:##防止坐标在-pi到pi时跳跃
                if self.heading_angle-self.desired_angle>math.pi/2:
                    heading_angle=self.heading_angle-math.pi*2
                elif self.heading_angle-self.desired_angle<-math.pi/2:
                    heading_angle=self.heading_angle+math.pi*2
                else:
                    heading_angle=self.heading_angle
                
                self.rudder=-self.rudder_controller.update(heading_angle,self.desired_angle)
                self.heading_angle=self.regular_angle(self.heading_angle)
                
            ## if we desire to turn about, set the rudder to the maximum angle, then the sailboat will choose the better diretion for turning.
            else:
                # print('AAAA')
                self.rudder=self.maxrudder*self.sign(math.sin(self.heading_angle-self.desired_angle))
                
        if self.velocity[0]<-0.02:    
            self.rudder=0
            # print('opp rudder',self.desired_angle,self.keeping_state)
        
    
    def sail_control(self):
        self.heading_angle=self.regular_angle(self.heading_angle)
        # print('if tacking',self.tacking_state)
        ## due to the wind's effect, the sail may not be able to reach its primary maxima
        if self.if_keeping:
            # print('keeping')
            if self.keeping_state==2:
                # print('AAAAAA')
                self.sail=self.maxsail
            elif self.keeping_state==5:
                if math.cos(self.heading_angle-self.true_wind[1])<-0.1:
                    self.sail=self.maxsail
                else:
                    self.sail=1
            
            elif self.keeping_state==1:
                 
                if self.heading_angle<-math.pi/2:
                    self.heading_angle+=math.pi*2
                if abs(self.heading_angle-math.pi/2)<=math.pi/4:
                    optimal_sail=0.2+(math.pi/4-abs(self.heading_angle-math.pi/2))*1.41
                else:
                    optimal_sail=0.2+(abs(self.heading_angle-math.pi/2)-math.pi/4)*0.47
                
                if self.desired_v>self.velocity[0]:
                    sail=optimal_sail+self.optimal_sail_adjustment
                
                    self.sail=min(self.maxsail,max(sail,0))
                else:
                    # print('BBBBBB')
                    self.sail=self.maxsail
        elif self.tacking_state=='is tacking':
            self.sail=self.maxsail
        elif self.if_force_turning==True:
            self.sail=self.maxsail
        else:
            self.sail_regular_control()

    def finding_optimal_sail(self):
        # self.optimal_sail_adjustment+=self.find_sail_sign*0.03
        self.optimal_sail_adjustment+=0
        if self.last_v>self.velocity[0]:
            self.find_sail_sign*=-1
        if self.optimal_sail_adjustment>0.2:
            self.optimal_sail_adjustment=0.2
            self.find_sail_sign*=-1
        if self.optimal_sail_adjustment<-0.2:
            self.optimal_sail_adjustment=-0.2
            self.find_sail_sign*=-1
        


    def sail_regular_control(self):
        global optimal_sail,limit_sail,obtained_angle   
        if self.heading_angle<-math.pi/2:
            self.heading_angle+=math.pi*2
        if abs(self.heading_angle-math.pi/2)<=math.pi/4:
            optimal_sail=0.25+(math.pi/4-abs(self.heading_angle-math.pi/2))*1.41
        else:
            optimal_sail=0.4+(abs(self.heading_angle-math.pi/2)-math.pi/4)*0.7
        
        optimal_sail+=self.optimal_sail_adjustment
        self.heading_angle=self.regular_angle(self.heading_angle)
        self.sail=min(self.maxsail,max(optimal_sail,0))
        
 
    def get_desired_angle(self,target_x,target_y):
        
        
        
        boat_to_target_angle=math.atan2(target_y-self.location[1],target_x-self.location[0])
        distance_st=math.sqrt(pow(target_y-self.location[1],2)+pow(target_x-self.location[0],2))
        #step2 ##this step is for the downwind case where the sailboat is not able to slow down.
        # The sailboat will therefore turn in a semicicle to arrive (upwind). 
        if distance_st>self.dT:
            self.if_keeping=False
            self.keeping_state=1
            self.go_to_target_area(boat_to_target_angle,distance_st)
        elif self.tacking_state=='not tacking' and self.if_force_turning==False:
            self.if_keeping=True
            self.keeping_in_target_area()
        self.tacking_detector()
        
    

    def go_to_target_area(self,boat_to_target_angle,distance_st):
        self.get_next_desired_angle(boat_to_target_angle,distance_st)
        
        self.tacking_if_I_can()
        
        
        if self.tacking_state=='is tacking':
            if self.time-self.start_tacking_time>0:
                self.desired_angle=self.tacking_angle
            # else:
            #     print('aaa',self.sail)
        
        else:
            
            if self.if_force_turning==True:
                self.desired_angle=self.regular_angle(self.true_wind[1])
                self.rudder=self.maxrudder*self.sign(math.sin(self.heading_angle-self.desired_angle))
                if self.velocity[0]<-0.1:    
                    self.rudder=-self.rudder
                if abs(self.regular_angle(self.heading_angle)-self.regular_angle(self.true_wind[1]))<0.5:
                    self.if_force_turning='go back to center'
                    self.go_to_center_start_time=self.time
            elif self.if_force_turning=='go back to center':
                
                self.desired_angle=self.go_to_center_angle
                if self.time<self.go_to_center_start_time+5:
                    
                    self.rudder=self.maxrudder*self.sign(math.sin(-math.pi/2-self.go_to_center_angle))
                    
                # if self.time<self.go_to_center_start_time+15:

                if self.time>self.go_to_center_start_time+50:
                    self.if_force_turning=False
            else:
                self.force_to_turn_when_hit_the_boundary(boat_to_target_angle)
        
        
    def tacking_if_I_can(self):
        if self.tacking_state != 'is tacking':
            if math.cos(self.heading_angle-self.true_wind[1])+math.cos(self.next_desired_angle-self.true_wind[1])<0:
                # print(self.next_desired_angle,self.heading_angle)
                if self.sign(math.sin(self.next_desired_angle-self.true_wind[1])) != self.sign(math.sin(self.heading_angle-self.true_wind[1])):
                    ###Yes, it's a tacking!
                    # print('Yes, it is a tacking!')
                
                    self.desired_v=3.5*0.3*abs(math.pi/2-self.heading_angle)/2/math.tan(self.maxrudder)
                    # print(self.desired_v)
                    if self.velocity[0]>self.desired_v:
                        ## I can tack
                        self.tacking_state='is tacking'
                        self.start_tacking_time=self.time
                        self.desired_angle=self.next_desired_angle
                        self.tacking_angle=self.regular_angle(self.next_desired_angle)
                        self.init_tacking_sign=self.sign(math.sin(self.heading_angle-math.pi/2))
                else:
                    self.desired_angle=self.next_desired_angle
            else:
                self.desired_angle=self.next_desired_angle
            self.desired_angle=self.regular_angle(self.desired_angle)
         
    def tacking_detector(self):
        if self.tacking_state=='is tacking':
            # print('init sign',self.init_tacking_sign,self.sign(math.sin(self.heading_angle-math.pi/2)))
            is_success=(self.init_tacking_sign !=self.sign(math.sin(self.heading_angle-math.pi/2)))
            if self.time-self.start_tacking_time>30 or self.velocity[0]<0.08 or is_success:
                if math.cos(self.heading_angle-self.true_wind[1])>-0.85:
                    self.tacking_state='not tacking'
                    if self.init_tacking_sign !=self.sign(math.sin(self.heading_angle-math.pi/2)):
                        print('tacked successfully')
                        self.optimal_sail_adjustment=0
                        self.d-=0.05
                    else:
                        print('failed tacking')
                        self.if_force_turning=True
                        self.go_to_center_angle=math.pi/2-self.sign(math.pi/2-self.tacking_angle)
                        self.d+=0.05

        

    def get_next_desired_angle(self,boat_to_target_angle,distance_st):
        self.next_desired_angle=boat_to_target_angle
        
        if distance_st<self.dM and distance_st>self.dT:
            if math.cos(boat_to_target_angle-self.true_wind[1])>0.4: ##not able to slow down
                
                if math.cos(boat_to_target_angle-(self.true_wind[1]+math.pi/2))>math.cos(boat_to_target_angle-(self.true_wind[1]-math.pi/2)):
                    self.next_desired_angle=-math.pi/2+boat_to_target_angle
                else:
                    self.next_desired_angle=math.pi/2+boat_to_target_angle
        if math.cos(self.true_wind[1]-self.next_desired_angle)<-0.71: ##exceed dead angle
            self.next_desired_angle=self.sign(math.sin(self.true_wind[1]-self.next_desired_angle))*0.98+math.pi/2
        # print(self.next_desired_angle,self.true_wind)

    def force_to_turn_when_hit_the_boundary(self,boat_to_target_angle):
        if self.location[0]>1.3 and self.location[0]<5.6 and self.location[1]>-3 and self.location[1]<7.8:
            print('',end='')
        else:
            if self.location[0]<2:
                self.go_to_center_angle=0.6
            elif  self.location[0]>3:
                self.go_to_center_angle=2.6
            
            ## turn to downwind direction
            if math.cos(self.heading_angle-boat_to_target_angle)<0:
                self.if_force_turning=True


    def keeping_in_target_area(self):
        boat_to_target_angle=math.atan2(self.target[1]-self.location[1],self.target[0]-self.location[0])
        distance_st=math.sqrt(pow(self.target[1]-self.location[1],2)+pow(self.target[0]-self.location[0],2))
        if distance_st*math.cos(self.true_wind[1]-boat_to_target_angle)>0.8*self.dT:
            self.keeping_state=4
            print('state 4')
        if self.keeping_state==1:
            self.state1(boat_to_target_angle)
                ## 1:lefthand side   2:righthand

        elif self.keeping_state==2:
            self.rudder=self.maxrudder*self.sign(math.sin(self.heading_angle-self.true_wind[1]-math.pi))
            self.final_heading_sign=self.sign(math.sin(self.true_wind[1]-math.pi-self.heading_angle))
            if self.final_heading_sign!=self.initial_heading_sign:
                if self.initial_heading_sign<0:
                    if self.heading_angle<math.pi-0.3:
                        self.keeping_state=3
                else:
                    self.keeping_state=3
                if self.velocity[0]>0.15:
                    self.d-=0.1
                print('State 3 parameter D',self.d)

            elif self.velocity[0]<0.05 and math.cos(self.heading_angle-self.true_wind[1])>-0.8:
                
                self.d+=0.1
                self.keeping_state=5
                self.init_tacking_sign=self.sign(math.sin(self.heading_angle-math.pi/2))
                print('Turning fail,State 5',self.d)

        
        elif self.keeping_state==3: ##尝试保持迎风
            if self.initial_heading_sign==1:
                self.desired_angle=self.regular_angle(self.true_wind[1]-math.pi)
            else:
                self.desired_angle=self.regular_angle(self.true_wind[1]-math.pi)-0.3
            if  self.location[1]<self.target[1] or abs(self.heading_angle-math.pi/2)>0.4:
                self.keeping_state=1
                print('3-state 1')
        
        elif self.keeping_state==4:
            target=[self.target[0]+math.cos(self.true_wind[1])*self.dT,self.target[1]+math.sin(self.true_wind[1])*self.dT]
            self.desired_angle=math.atan2(target[1]-self.location[1],target[0]-self.location[0])
            if distance_st*math.cos(self.true_wind[1]-boat_to_target_angle)<0:
                self.keeping_state=1
                print('4-State 1')
        
        elif self.keeping_state==5:
            
            self.rudder=-self.maxrudder*self.init_tacking_sign
            if math.cos(self.heading_angle-(self.true_wind[1]-math.pi-self.init_tacking_sign))>0.5:
                self.keeping_state=1
                
                print('5-State 1')
 
    def state1(self,boat_to_target_angle):
        self.desired_v=self.d*0.3*abs(self.true_wind[1]-math.pi-self.desired_angle)**1.5/2/math.tan(self.maxrudder)
        if self.desired_v<0.4:
            self.desired_v=0.4
        elif self.desired_v>0.55:
            self.desired_v=0.55
        if math.sin(self.true_wind[1]-self.heading_angle)>0:
            self.desired_angle=self.regular_angle(self.true_wind[1]-math.pi*0.7)
        else:
            self.desired_angle=self.regular_angle(self.true_wind[1]+math.pi*0.7)
        if self.desired_v>self.velocity[0]:
            a=2
            b=2.4
            # print(self.desired_v)
            total_distance=1.5*(-a*b*math.log(1-b/a*self.desired_v)-b*self.desired_v)/b**2
            
            remanent_distance=total_distance-1.5*(-a*b*math.log(1-b/a*self.velocity[0])-b*self.velocity[0])/b**2
            
            # print(total_distance,remanent_distance)
            x=remanent_distance*math.cos(self.desired_angle)+0.85*self.sign(math.cos(self.desired_angle))
            y=(0.6*remanent_distance*math.sin(self.desired_angle)+0.6)
            print([x,remanent_distance,self.location[0]])
            print([self.location[0]+x,self.location[1]+y],(self.location[0]+x-self.target[0])**2+(self.location[1]+y-self.target[1])**2,self.velocity[0]>self.desired_v)
        else:
            x=0.75*self.sign(math.cos(self.desired_angle))
            y=0.6
        
        if (self.location[0]+x-self.target[0])**2+(self.location[1]+y-self.target[1])**2>self.dT**2:
            ##即将出边界
            print('out!!',[x,y],self.location)
            print([self.location[0]+x,self.location[1]+y],(self.location[0]+x-self.target[0])**2+(self.location[1]+y-self.target[1])**2)
            print(self.desired_v,self.velocity[0])
            if 4.5<self.location[1] and abs(self.location[0]-3)<0.4:
                self.keeping_state=5
                print('state 1- State 5')
                self.init_tacking_sign=self.sign(math.sin(self.heading_angle-math.pi/2))
                self.sail=self.maxsail
                self.sleep_time=4
            else:
                self.sleep_time=2
                self.keeping_state=2
                self.initial_heading_sign=self.sign(math.sin(self.true_wind[1]-math.pi-self.heading_angle))
        else:
            # print('111')
            if self.velocity[0]-self.desired_v>-0.05:
                # print('222')
                if math.cos(self.heading_angle-boat_to_target_angle)<0:
                    # print('333')
                    self.sleep_time=self.get_sleeping_time(y,x)
                    if self.sleep_time>2:
                        self.sleep_time=2
                    print('sleep',self.sleep_time)
                    self.sail=self.maxsail
                    self.keeping_state=2
                    print('state 2',self.velocity[0],self.desired_v)
                    self.initial_heading_sign=self.sign(math.sin(self.true_wind[1]-math.pi-self.heading_angle))

    def get_sleeping_time(self,y,x):
        c=self.dT
        C=self.regular_angle(self.heading_angle)-math.atan2(self.target[1]-self.location[1]-y,self.target[0]-self.location[0]-x)
        a=math.sqrt((self.target[1]-self.location[1]-y)**2+(self.target[0]-self.location[0]-x)**2)
        b1=max(abs(a*math.cos(C)+math.sqrt((a*math.cos(C))**2+c**2-a**2))-0.4,0)
        b2=max(abs(a*math.cos(C)-math.sqrt((a*math.cos(C))**2+c**2-a**2))-0.4,0)
        b=min(b1,b2)
        print(a,b,c,C,a*math.cos(C)**2,c**2-a**2)
        return int(b*5)
    def updata_pos(self,x,y,heading_angle,roll):
        
        last_x=self.location[0]
        last_y=self.location[1]
        last_heading=self.heading_angle
        last_roll=self.roll

        self.location[0]=x
        self.location[1]=y
        self.heading_angle=heading_angle
        self.roll=roll
        self.get_velocity(x,last_x,y,last_y,heading_angle,last_heading,last_roll)
        self.course_angle=math.atan2(self.location[1]-last_y,self.location[0]-last_x)
        self.regular_all_angle()
    
    def get_velocity(self,x,last_x,y,last_y,heading_angle,last_heading,last_roll):
        del_x=x-last_x
        del_y=y-last_y
        if self.time%8==0:
            self.last_v=self.velocity[0]
        elif self.time%16==7:
            self.finding_optimal_sail()
        v=(del_x*math.cos(self.heading_angle)+del_y*math.sin(self.heading_angle))*self.frequency
        u=(-del_x*math.sin(self.heading_angle)+del_y*math.cos(self.heading_angle))*self.frequency
        w=(heading_angle-last_heading)*self.frequency
        p=(self.roll-last_roll)*self.frequency
        
        ### due to the noise, the velocity we choose is the mean value of the velocities in 0.7 second.
        self.v_list.pop(0)
        if abs(v)>3:
            v=self.v_list[3]
        self.v_list.append(v)

        self.u_list.pop(0)
        if abs(u)>1:
            u=self.u_list[3]
        self.u_list.append(u)
        self.w_list.pop(0)
        if abs(w)>3.5:
            w=self.w_list[3]
        self.w_list.append(w)
        self.p_list.pop(0)
        if abs(p)>2:
            p=self.p_list[3]
        self.p_list.append(p)
        self.velocity[0]=0
        self.velocity[1]=0
        self.angular_velocity=0
        self.roll_angular_velocity=0
        
        for i in range (0,5):
            self.velocity[0]+=self.v_list[i]/5
            self.velocity[1]+=self.u_list[i]/5
            self.angular_velocity+=self.w_list[i]/5
            self.roll_angular_velocity+=self.p_list[i]/5
        

    def get_app_wind(self):
        
        ###this part is different from the paper since there might be something wrong in the paper
        ###get coordinates of true wind
        
        self.app_wind=[self.true_wind[0]*math.cos(self.true_wind[1]-self.heading_angle)-self.velocity[0],
                        self.true_wind[0]*math.sin(self.true_wind[1]-self.heading_angle)-self.velocity[1]]
        ###convert into polar system
        angle=math.atan2(self.app_wind[1],self.app_wind[0])
        self.app_wind=[math.sqrt(pow(self.app_wind[1],2)+pow(self.app_wind[0],2)),angle]
        return self.app_wind


## all angle should be modified into the range [0,2*pi)   
    def regular_angle(self,angle):
        
        while angle>math.pi:
            angle-=math.pi*2
        while angle<-math.pi:
            angle+=math.pi*2
        return angle


    def sign(self,p):
        
        if p>0:
            return 1
        elif p==0:
            return 0
        else:
            return -1