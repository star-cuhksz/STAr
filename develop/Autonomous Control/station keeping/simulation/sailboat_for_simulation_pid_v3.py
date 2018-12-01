import math
import random
import time
from pid2 import PID


class sailboat:


    def __init__(self,velocity=[0,0],choosen_angle=0,heading_angle=0,course_angle=0,desired_angle=0,angular_velocity=0,location=[0,0],
    rudder=0,sail=0,jibsail=0,sample_time=0.1,acc_v=0,acc_u=0,acc_w=0,desired_acc=0):
    ####    all the units of angles are rad 
        self.velocity=velocity ###[v,u], where v is the heading angle of the sailboat 
        self.heading_angle=heading_angle
        self.course_angle=course_angle  
        self.desired_angle=desired_angle    
        self.angular_velocity=angular_velocity   ## w
        self.location=location   ###[x,y]
        self.rudder=rudder       ### the positive angle is corresponding to counterclockwise
        self.sail=sail           ### the positive angle is corresponding to counterclockwise
        self.choosen_angle=choosen_angle        
        #self.jibsail=jibsail    ### to be continued
        self.acc_v=acc_v        
        self.acc_u=acc_u
        self.acc_w=acc_w
        self.target=[3,6]     ###the center of target area[x,y]   self.dM=10,which is the radius of the pre-arrived area ,self.dT=5,which is r of target area 
        self.desired_acc=desired_acc            

        self.p1=0.01        ##drift coefficient####relative big for the plastic sailboat
        self.p2=2.5         ##tangential friction
        self.p3=0.8        ##angular friction
        self.p4=1.5         ##sail lift
        self.p5=30        ##rudder lift
        self.p6=0.05         ##distance to sail
        self.p7=0.05         ##distance to mast
        self.p8=0.25           ##distance to rudder
        self.p9=3         ##mass of boat
        self.p10=0.3        ##moment of inertia
        self.p11=0.3       ##rudder break coefficient 
        self.dT=0.7
        self.dM=1.4
        self.boat_size=0.1   ##which equals that the length of the boat is 0.3m

        self.maxrudder=math.pi/4  ##max angle of rudder
        self.maxsail=math.pi/12*5
        self.true_wind=[5,math.pi*3/2]       ##[wind speed, direction]
        self.app_wind=[0,0]                 ##[wind speed, direction]
        self.sample_time=0.01               ##time for every single update
        self.ks=50              ###need to be adjusted ###
        self.aligned_p=0.1       ####need to be adjusted ##about 15 degrees of the mini sailboat
        
        self.q=-1               ##the parameter for tacking which is 1 or -1
        self.time=0

        self.rudder_controller=PID()
        self.n=0.1
        self.if_acc=0
        # self.if_tacking=0

        #this part is to add the boundary
        target_boat_angle=math.atan2(self.target[1]-self.location[1],self.target[0]-self.location[0])
        self.x_value=self.sign(math.cos(target_boat_angle))
        self.y_value=self.sign(math.sin(target_boat_angle))
    
    def get_tacking_state(self,last_angle):

        if math.cos(last_angle-self.true_wind[1])+math.cos(self.desired_angle-self.true_wind[1])<0 and math.cos(last_angle-self.true_wind[1])>-0.8:
            
            if self.sign(math.sin(self.desired_angle-self.true_wind[1]))!=self.sign(math.sin(last_angle-self.true_wind[1])) and self.velocity[0]<0.3:
                
                self.desired_angle=self.true_wind[1]*2-self.desired_angle
                
                self.desired_angle=self.regular_angle(self.desired_angle)
                
          
        
    def get_true_wind(self):
        
        
        # self.true_wind=[10+5*math.sin(6.28*self.time),math.pi/2+math.pi/12*math.sin(6.28*self.time)]
        coo_true_wind=[self.true_wind[0]*math.cos(self.true_wind[1]),self.true_wind[0]*math.sin(self.true_wind[1])]
        return self.true_wind,coo_true_wind
        
    def regular_angle(self,angle):
        
        while angle>math.pi*2:
            angle-=math.pi*2
        while angle<0:
            angle+=math.pi*2
        return angle

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

    def choose_angle(self):
        ##owing to the course angle may not be equal to the heading angle, if the difference is large, we use the heading angle
        ## the goal of this part is not so clear and needs some discussion
        self.course_angle=self.regular_angle(self.course_angle)
        if abs(self.course_angle-self.heading_angle)<math.pi/18:
            self.choosen_angle=self.course_angle
        else:
            self.choosen_angle=self.heading_angle
        

    def rudder_control(self):
        self.choosen_angle=self.regular_angle(self.choosen_angle)
        
        self.desired_angle=self.regular_angle(self.desired_angle)
        if math.cos(self.choosen_angle-self.desired_angle)>0:
            if self.choosen_angle-self.desired_angle>math.pi/2:
                choosen_angle=self.choosen_angle-math.pi*2
            elif self.choosen_angle-self.desired_angle<-math.pi/2:
                choosen_angle=self.choosen_angle+math.pi*2
            else:
                choosen_angle=self.choosen_angle
            # print([choosen_angle,self.desired_angle])
            self.rudder=-self.rudder_controller.update(choosen_angle,self.desired_angle)
            # print('pid',self.choosen_angle,self.desired_angle)
            
        ## if we desire to turn about, set the rudder to the maximum angle
        ## this part garantee the sailboat will choose the better diretion for turning.
        else:
            
            self.rudder=self.maxrudder*self.sign(math.sin(self.choosen_angle-self.desired_angle))
            # print('normal',self.rudder,self.choosen_angle)
        if self.velocity[0]<0:
            self.rudder=-self.rudder

    def sign(self,p):
        if p>0:
            return 1
        elif p==0:
            return 0
        else:
            return -1

    def sail_control(self):
        global optimal_sail,limit_sail,obtained_angle
        ## due to the wind's effect, the sail may not be able to reach its primary maxima
        # print(self.app_wind)
        pratical_sail_max=min(abs(math.pi-abs(self.app_wind[1])),self.maxsail)
        
        ##not that angular accelaration of the sail instead of the boat
        angular_acc=-self.ks*(self.desired_acc-self.acc_v)
        obtained_angle=max(angular_acc*self.sample_time+abs(self.sail),0)###the angle of sail
        limit_sail=max(pratical_sail_max-self.aligned_p,0)
        ### if we want the sailboat to speed up, we choose the optimal angle
        if angular_acc<0:
            self.if_acc=1
            optimal_sail=math.pi/4*(math.cos(self.true_wind[1]-self.desired_angle)+1)
            
            
            self.sail=-self.sign(self.app_wind[1])*min(self.maxsail,max(obtained_angle,min(abs(optimal_sail),limit_sail)))
            # print('acc',obtained_angle,abs(optimal_sail),limit_sail,self.acc_v)
        else:
            ### we put the sail to limit to slow down
            self.if_acc=0
            self.sail=-self.sign(self.app_wind[1])*min(pratical_sail_max,obtained_angle)
            # print('deacc',obtained_angle,pratical_sail_max,self.app_wind[1])

            
    def get_desired_acc(self,target_x,target_y):
        
        kp=0.25  ### need adjustment
        kv=1.2   ### need adjustment
        ### the prove of the stability is shown in the last page of the paper
        target_boat_angle=math.atan2(target_y-self.location[1],target_x-self.location[0])
        v0=max(0,self.velocity[1]*math.tan(self.heading_angle))
        ###distance between the sailboat and the center of the target
        distance_st=math.sqrt(pow(target_y-self.location[1],2)+pow(target_x-self.location[0],2))
        
        self.desired_acc=-kv*(self.velocity[0]-v0)+kp*distance_st
    


    
    def arrive(self,target_x,target_y):
        last_angle=self.desired_angle
        
        ### the statagy for reaching the target area
        #step1
        boat_to_target_angle=math.atan2(target_y-self.location[1],target_x-self.location[0])
        #step2 ##this case is for downwind
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
        else:
            goal_angle=boat_to_target_angle
        

        #step 3 ##this is for the upwind case
        dead_angle=math.pi/5
        ##if not exceeding dead angle
        if math.cos(self.true_wind[1]-goal_angle)+math.cos(math.pi/2-dead_angle)>0:
            self.desired_angle=goal_angle
            ###prepare for reaching the dead angle, determine which way is more convinient to tack
            if math.cos(goal_angle-(self.true_wind[1]+math.pi-dead_angle))>math.cos(goal_angle-(self.true_wind[1]+math.pi+dead_angle)):
                self.q=1
            else:
                self.q=-1
        else:
            if distance_st>self.dM:
                if self.location[0]<0.8:
                    self.x_value=1
                
                elif self.location[0]>5.5:
                    self.x_value=-1
                if self.location[1]<2:
                    self.y_value=1
                
                elif self.location[1]>8:
                    self.y_value=-1
            ##if exceeding the dead angle,change the desired angle
                # self.desired_angle=self.true_wind[1]+math.pi+self.q*(math.pi/2-dead_angle)
                self.desired_angle=math.atan2(self.y_value*0.8,self.x_value)
        
        #step 4 ##upwind strategy for inside the target area. aim to keep the heading angle being oppisite of the wind direction 
            # print(self.app_wind[1])
    ###however, in the practical case, the boat cannot stay in the target area forever, therefore, a plan for re-arriving the target area is proposed
    ###tacking if the velocity is sufficient
        # self.desired_angle=self.regular_angle(self.desired_angle)
        self.get_tacking_state(last_angle)
        if distance_st<self.dT:
            self.keeping()
            # if self.velocity[0]>0:
            #     self.desired_angle=self.true_wind[1]+math.pi
            #     self.sail=-self.sign(self.app_wind[1])*min(self.maxsail,abs(math.pi-abs(self.app_wind[1])))
            # elif self.velocity[0]<=0:
            #     self.desired_angle=self.true_wind[1]+math.pi-dead_angle*self.sign(self.velocity[1])
            #     self.sail=-self.sign(self.app_wind[1])*min(abs(optimal_sail),limit_sail)
    
    def keeping(self):
        boat_to_target_angle=math.atan2(self.target[1]+0.2-self.location[1],self.target[0]-self.location[0])
        if math.cos(boat_to_target_angle-self.true_wind[1])<0:
            self.desired_angle=boat_to_target_angle
            self.regular_angle(self.desired_angle)
            if self.desired_angle<0.5:
                self.desired_angle=1.57
            elif self.desired_angle>2.65:
                self.desired_angle=1.57
            elif self.desired_angle<1.57 and self.desired_angle>0.8:
                self.desired_angle=0.8
            elif self.desired_angle>1.57 and self.desired_angle<2.3:
                self.desired_angle=2.3
            if self.velocity[0]<0.1:
                
                self.sail=-self.sign(self.app_wind[1])*min(self.maxsail,abs(optimal_sail),limit_sail)
            
        else:
            self.desired_angle=self.true_wind[1]-math.pi
            
            self.sail=-self.sign(self.app_wind[1])*min(self.maxsail,abs(math.pi-abs(self.app_wind[1])))

    
    
    def updata_pos(self):
        ### this part is simply use the sailboat dynamic to simulate the position for the next moment.
        
        
        g_rv=self.p5*self.velocity[0]*abs(self.velocity[0])*math.sin(self.rudder)
        g_ru=self.p5*self.velocity[1]*abs(self.velocity[1])*math.cos(self.rudder)
        g_s=self.p4*self.app_wind[0]*math.sin(self.sail-self.app_wind[1])

        self.acc_v=(g_s*math.sin(self.sail)-g_rv*self.p11*math.sin(self.rudder)-self.p2*self.velocity[0]*abs(self.velocity[0])
        +self.p1*pow(self.app_wind[0],2)*math.cos(self.app_wind[1]))/self.p9
        # if self.acc_v>0:
        print(g_s*math.sin(self.sail),-g_rv*self.p11*math.sin(self.rudder),-self.p2*self.velocity[0]*abs(self.velocity[0]),self.p1*pow(self.app_wind[0],2)*math.cos(self.app_wind[1]),self.velocity[0])
        self.acc_u=(-g_ru*self.p11*math.cos(self.rudder)-self.p2*self.velocity[1]*abs(self.velocity[1])
        +self.p1*pow(self.app_wind[0],2)*math.sin(self.app_wind[1])/6)/self.p9

        self.acc_w=(g_s*(self.p6-self.p7*math.cos(self.sail))-g_rv*self.p8*math.cos(self.rudder)
        -self.p3*self.angular_velocity*self.velocity[0]*self.sign(self.velocity[0]))/self.p10
        # print(g_s*(self.p6-self.p7*math.cos(self.sail)),-g_rv*self.p8*math.cos(self.rudder),-self.p3*self.angular_velocity*self.velocity[0],self.acc_w,self.angular_velocity)
        self.velocity[0]+=self.sample_time*self.acc_v
        self.velocity[1]+=self.sample_time*self.acc_u
        self.angular_velocity+=self.sample_time*self.acc_w

        # self.velocity[0]+=random.gauss(0,self.velocity[0]/10)
        # self.velocity[1]+=random.gauss(0,self.velocity[1]/10)
        # self.angular_velocity+=random.gauss(0,self.angular_velocity/10)


        last_x=self.location[0]
        last_y=self.location[1]

        self.location[0]+=(self.velocity[0]*math.cos(self.heading_angle)-self.velocity[1]*math.sin(self.heading_angle))*self.sample_time
        self.location[1]+=(self.velocity[1]*math.cos(self.heading_angle)+self.velocity[0]*math.sin(self.heading_angle))*self.sample_time
        self.heading_angle+=self.angular_velocity*self.sample_time
        # print(g_s*(self.p6-self.p7*math.cos(self.sail)),-g_rv*self.p8*math.cos(self.rudder),self.p3*self.angular_velocity*self.velocity[0])
        
        # print('location',self.location,'heading',self.heading_angle,'velocity',self.velocity)
        self.course_angle=math.atan2(self.location[1]-last_y,self.location[0]-last_x)
    
    def to_next_moment(self):
        global n
        self.time+=self.sample_time
        
        
        self.get_app_wind()
        
        self.updata_pos()
        
        self.choose_angle()
        
        self.rudder_control()
        
        self.get_desired_acc(self.target[0],self.target[1])
        
        self.sail_control()
        
        self.arrive(self.target[0],self.target[1])
        
        return self.location,self.rudder,self.sail,self.desired_angle,self.heading_angle
