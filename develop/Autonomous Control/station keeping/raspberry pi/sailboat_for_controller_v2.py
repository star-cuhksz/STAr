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
    rudder=0,sail=0,sample_time=0.1,target=[3,5],IMU_sample_time=0.1,data_base_sample_time=0.1):
    ####    all the units of angles are rad 
        self.velocity=velocity ###[v,u], where v is the heading angle of the sailboat 
        self.heading_angle=heading_angle
        self.course_angle=course_angle  
        self.desired_angle=desired_angle    
        self.angular_velocity=angular_velocity   ## w
        self.location=location   ###[x,y]
        self.rudder=rudder       ### the positive angle is corresponding to counterclockwise
        self.sail=sail           ### the positive angle is corresponding to counterclockwise
        self.choosen_angle=0       
        
        self.target=target    ###the center of target area[x,y]   self.dM=10,which is the radius of the pre-arrived area ,self.dT=5,which is r of target area 
        self.desired_acc=0           
        self.frequency=10
        self.dT=1        ## radius of target area
        self.dM=1.8         ## radius of pre arrive
        self.desired_v=0

        self.maxrudder=math.pi/4  ##max angle of rudder
        self.maxsail=math.pi/12*5

        self.true_wind=[5,math.pi*3/2]       ##[wind speed, direction]
        self.app_wind=[0,0]                 ##[wind speed, direction]
        self.sample_time=0.01               ##time for every single update
                      ###need to be adjusted ###
        
        
       
        self.time=0

        self.rudder_controller=PID()
        self.sail_speed_controller=PID(0.1,0.01,0.05)
        self.d=4
        self.if_acc=0
        #this part is to add the boundary
        self.x_value=1
        self.y_value=1

        self.flag=False
        self.if_keeping=False
        self.keeping_state=1  ##1: before turning 2: turning 3:recover 4:go back
        self.v_list=[0]*7
        self.u_list=[0]*7
        self.w_list=[0]*7

        
    ## predict the state for next moment and make decision  
    def update_state(self):
        global n
        self.time+=1
        if self.time>3000:
            self.flag=True  #Stop the program

        self.rudder_control()    
        
        self.sail_control()
        
        self.get_desired_angle(self.target[0],self.target[1])
        
        if self.time%10==0:
            print('rudder',self.rudder,'sail',self.sail,'desired_angle',self.desired_angle)
        return self.rudder,self.sail,self.desired_angle

    def rudder_control(self):
        self.get_app_wind()
        self.choose_angle()
        self.get_desired_acc(self.target[0],self.target[1])


        if self.keeping_state!=2:  
            self.choosen_angle=self.regular_angle(self.choosen_angle)
            
            self.desired_angle=self.regular_angle(self.desired_angle)
            if math.cos(self.choosen_angle-self.desired_angle)>0:
                if self.choosen_angle-self.desired_angle>math.pi/2:
                    choosen_angle=self.choosen_angle-math.pi*2
                elif self.choosen_angle-self.desired_angle<-math.pi/2:
                    choosen_angle=self.choosen_angle+math.pi*2
                else:
                    choosen_angle=self.choosen_angle
                
                self.rudder=-self.rudder_controller.update(choosen_angle,self.desired_angle)
                
                
            ## if we desire to turn about, set the rudder to the maximum angle, then the sailboat will choose the better diretion for turning.
            else:
                
                self.rudder=self.maxrudder*self.sign(math.sin(self.choosen_angle-self.desired_angle))
                
            if self.velocity[0]<0:    
                self.rudder=-self.rudder
    
    def sail_control(self):
        
        ## due to the wind's effect, the sail may not be able to reach its primary maxima
        if self.if_keeping:
            if self.keeping_state==2:
                self.sail=self.maxsail
            elif self.keeping_state==1:
                if math.cos(self.true_wind[1]-self.heading_angle)>0.6:
                    optimal_sail=self.maxsail
                elif math.cos(self.true_wind[1]-self.heading_angle)<-0.73:
                    optimal_sail=self.maxsail
                else:
                    optimal_sail=0.25+(abs(self.heading_angle-self.true_wind[1]+math.pi)-math.pi/4)*0.75
                # optimal_sail=abs(math.pi/4*(math.cos(self.true_wind[1]-self.desired_angle)+1))
                if self.desired_v>self.velocity[0]:
                    sail=optimal_sail
                else:
                    sail=(optimal_sail+self.maxsail)/2-(self.desired_v-self.velocity[0])*0.8
                self.sail=min(self.maxsail,max(sail,0))
        else:
            self.sail_regular_control()
        
    def sail_regular_control(self):
        global optimal_sail,limit_sail,obtained_angle   
        ##not that angular accelaration of the sail instead of the boat
        angular_acc=-50*self.desired_acc
        obtained_angle=max(angular_acc/self.frequency+abs(self.sail),0)###the angle of sail
       
        ### if we want the sailboat to speed up, we choose the optimal angle
        if angular_acc<0:
            self.if_acc=1
            if math.cos(self.true_wind[1]-self.heading_angle)>0.6:
                optimal_sail=self.maxsail
            elif math.cos(self.true_wind[1]-self.heading_angle)<-0.73:
                optimal_sail=self.maxsail
            else:
                optimal_sail=0.25+(abs(self.heading_angle-self.true_wind[1]+math.pi)-math.pi/4)*0.7
            
            
            self.sail=min(self.maxsail,max(obtained_angle,abs(optimal_sail)))
           
        else:
            ### we put the sail to limit to slow down
            self.if_acc=0
            self.sail=min(self.maxsail,obtained_angle)
        
    


    
    def get_desired_angle(self,target_x,target_y):
        last_angle=self.desired_angle
        
        ### the statagy for reaching the target area
        #step1
        boat_to_target_angle=math.atan2(target_y-self.location[1],target_x-self.location[0])
        distance_st=math.sqrt(pow(target_y-self.location[1],2)+pow(target_x-self.location[0],2))
        #step2 ##this step is for the downwind case where the sailboat is not able to slow down.
        # The sailboat will therefore turn in a semicicle to arrive (upwind). 
        goal_angle=self.step2(target_x,target_y,boat_to_target_angle)
        

        #step 3 ##this is for the upwind case. 
        # If the goal angle is in the dead zone, the sailboat will nevigate in a proper direction.
        
        self.step3(goal_angle,distance_st)
        
    ###tacking if the velocity is sufficient. Otherwise, the desired angle will remain unchanged.
        self.get_tacking_state(last_angle)
        
        if distance_st<self.dT:
            self.if_keeping=True
            self.keeping()
        else:
            self.if_keeping=False

        ###go back before the program stops
        if self.time>2800:
            self.desired_angle=math.atan2(0-self.location[1],3.5-self.location[0])    

    
    def step2(self,target_x,target_y,boat_to_target_angle):
        distance_st=math.sqrt(pow(target_y-self.location[1],2)+pow(target_x-self.location[0],2))

        #determine if the sailboat is in the pre-arrive area and if it is convinient for the sailboat to turn round and move upwind to the target area
        if distance_st<self.dM and distance_st>self.dT and math.cos(boat_to_target_angle-self.true_wind[1])>0:
            #if it's in the area and not convinient to, then change the desired orientation to a perpendicular direction
            afa=math.atan2(target_y-self.location[1],target_x-self.location[0])
            # print(self.velocity[0])
            if math.cos(afa-(self.true_wind[1]+math.pi/2))>math.cos(afa-(self.true_wind[1]-math.pi/2)):
                goal_angle=-math.pi/2+boat_to_target_angle
            else:
                goal_angle=math.pi/2+boat_to_target_angle
            self.keeping_state=1
            self.if_keeping=False
        else:
            goal_angle=boat_to_target_angle
        return goal_angle


    def step3(self,goal_angle,distance_st):
        dead_angle=math.pi/4.5
        if math.cos(self.true_wind[1]-goal_angle)+math.cos(math.pi/2-dead_angle)>0:##if not exceeding dead angle
            self.desired_angle=goal_angle
        else:##if exceeding the dead angle,change the desired angle
            if distance_st>self.dM:
                if self.location[0]<1.6:
                    self.x_value=1
                
                elif self.location[0]>5:
                    self.x_value=-1
                if self.location[1]<2:
                    self.y_value=1
                
                elif self.location[1]>6:
                    self.y_value=-1
            
                self.desired_angle=math.atan2(self.y_value*0.8,self.x_value)

    def keeping(self):
        boat_to_target_angle=math.atan2(self.target[1]-self.location[1],self.target[0]-self.location[0])
        distance_st=math.sqrt(pow(self.target[1]-self.location[1],2)+pow(self.target[0]-self.location[0],2))
        if distance_st*math.cos(self.true_wind[1]-boat_to_target_angle)>0.6*self.dT:
            self.keeping_state=4
        if self.keeping_state==1:
            self.desired_v=self.d*0.3*abs(self.true_wind[1]-math.pi-self.desired_angle)/2/math.tan(self.maxrudder)
            if math.sin(self.true_wind[1]-self.heading_angle)>0:
                self.desired_angle=self.regular_angle(self.true_wind[1]-math.pi*0.7)
            else:
                self.desired_angle=self.regular_angle(self.true_wind[1]+math.pi*0.7)

            if abs(self.velocity[0]-self.desired_v)<0.1:
                self.keeping_state=2
                print('state 2')
                initial_heading_sign=self.sign(math.sin(self.true_wind[1]-self.heading_angle))
                ## 1:lefthand side   2:righthand

        elif self.keeping_state==2:
            self.rudder=self.maxrudder*self.sign(math.sin(self.heading_angle-self.desired_angle))
            if self.velocity[0]<0.05 or abs(self.regular_angle(self.heading_angle+math.pi)-self.true_wind[1])<0.05:
                self.keeping_state=3
                if self.velocity[0]<0.05 and abs(self.regular_angle(self.heading_angle+math.pi)-self.true_wind[1])>0.15:
                    self.d+=0.1
                elif abs(self.regular_angle(self.heading_angle+math.pi)-self.true_wind[1])<0.05 and self.velocity[0]>0.15:
                    self.d-=0.1
                print('State 3 parameter D',self.d)

        
        elif self.keeping_state==3:
            self.desired_angle=self.regular_angle(self.true_wind[1]-math.pi)
            if self.location[1]<self.target[1]:
                self.keeping_state=1
                print('state 1')
        
        elif self.keeping_state==4:
            target=[self.target[0]+math.cos(self.true_wind[1])*self.dT,self.target[1]+math.sin(self.true_wind[1])*self.dT]
            self.desired_angle=math.atan2(target[1]-self.location[1],target[0]-self.location[0])
            if distance_st*math.cos(self.true_wind[1]-boat_to_target_angle)<0:
                self.keeping_state=1
                print('State 1')
            
 
    def updata_pos(self,x,y,heading_angle):
        
        last_x=self.location[0]
        last_y=self.location[1]
        last_heading=self.heading_angle

        self.location[0]=x
        self.location[1]=y
        self.heading_angle=heading_angle
        self.get_velocity(x,last_x,y,last_y,heading_angle,last_heading)
        self.course_angle=math.atan2(self.location[1]-last_y,self.location[0]-last_x)
    
    def get_velocity(self,x,last_x,y,last_y,heading_angle,last_heading):
        del_x=x-last_x
        del_y=y-last_y

        v=(del_x*math.cos(self.heading_angle)+del_y*math.sin(self.heading_angle))*self.frequency
        u=(-del_x*math.sin(self.heading_angle)+del_y*math.cos(self.heading_angle))*self.frequency
        w=(heading_angle-last_heading)*self.frequency
        
        ### due to the noise, the velocity we choose is the mean value of the velocities in 0.7 second.
        self.v_list.pop(0)
        if abs(v)>3:
            v=self.v_list[5]
        self.v_list.append(v)
        self.u_list.pop(0)
        if abs(u)>1:
            u=self.u_list[4]
        self.u_list.append(u)
        self.w_list.pop(0)
        if abs(w)>3.5:
            w=self.w_list[4]
        self.w_list.append(w)
        self.velocity[0]=0
        self.velocity[1]=0
        self.angular_velocity=0
        for i in range (0,7):
            self.velocity[0]+=self.v_list[i]/7
            self.velocity[1]+=self.u_list[i]/7
            self.angular_velocity+=self.w_list[i]/7
        

    def get_app_wind(self):
        
        ###this part is different from the paper since there might be something wrong in the paper
        ###get coordinates of true wind
        self.true_wind=self.get_true_wind()[0]


        self.app_wind=[self.true_wind[0]*math.cos(self.true_wind[1]-self.heading_angle)-self.velocity[0],
                        self.true_wind[0]*math.sin(self.true_wind[1]-self.heading_angle)-self.velocity[1]]
        ###convert into polar system
        angle=math.atan2(self.app_wind[1],self.app_wind[0])
        self.app_wind=[math.sqrt(pow(self.app_wind[1],2)+pow(self.app_wind[0],2)),angle]
        return self.app_wind

##owing to the course angle may not be equal to the heading angle, if the difference is large, we use the heading angle
## the goal of this part is not so clear and needs some discussion
    def choose_angle(self):
        
        self.course_angle=self.regular_angle(self.course_angle)
        if abs(self.course_angle-self.heading_angle)<math.pi/18:
            self.choosen_angle=self.course_angle
        else:
            self.choosen_angle=self.heading_angle      

    def get_tacking_state(self,last_angle):
        ### tack only if the speed is sufficient
        if math.cos(last_angle-self.true_wind[1])+math.cos(self.desired_angle-self.true_wind[1])<0 and math.cos(last_angle-self.true_wind[1])>-0.8:
            
            if self.sign(math.sin(self.desired_angle-self.true_wind[1]))!=self.sign(math.sin(last_angle-self.true_wind[1])) and self.velocity[0]<0.3:
                
                self.desired_angle=self.true_wind[1]*2-self.desired_angle
                
                self.desired_angle=self.regular_angle(self.desired_angle)
                        
    def get_true_wind(self):
        
        
        # self.true_wind=[10+5*math.sin(6.28*self.time),math.pi/2+math.pi/12*math.sin(6.28*self.time)]
        coo_true_wind=[self.true_wind[0]*math.cos(self.true_wind[1]),self.true_wind[0]*math.sin(self.true_wind[1])]
        return self.true_wind,coo_true_wind

## all angle should be modified into the range [0,2*pi)   
    def regular_angle(self,angle):
        
        while angle>math.pi*2:
            angle-=math.pi*2
        while angle<0:
            angle+=math.pi*2
        return angle

##Get desired acceleration
    def get_desired_acc(self,target_x,target_y):
        
        kp=0.25  ### need adjustment
        kv=1.2   ### need adjustment
        ### the prove of the stability is shown in the last page of the paper
        target_boat_angle=math.atan2(target_y-self.location[1],target_x-self.location[0])
        v0=max(0,self.velocity[1]*math.tan(self.heading_angle))
        ###distance between the sailboat and the center of the target
        distance_st=math.sqrt(pow(target_y-self.location[1],2)+pow(target_x-self.location[0],2))
        
        self.desired_acc=-kv*(self.velocity[0]-v0)+kp*distance_st

    def sign(self,p):
        
        if p>0:
            return 1
        elif p==0:
            return 0
        else:
            return -1