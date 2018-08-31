import time
import math

class sailboat:


    def __init__(self,volocity=[20,0],angular_volocity=0,location=[0,0],rudder=90,sail=1,sample_time=0.1):
        self.volocity=volocity
        self.angular_volocity=angular_volocity
        self.location=location
        self.rudder=rudder
        self.sail=sail
        
        self.sample_time=0.1
    
    def get_parameter(self,volocity,angular_volocity,location,sail,rudder):
        self.volocity=volocity
        self.angular_volocity=angular_volocity
        self.location=location
        self.sail=sail
        self.rudder=rudder
# predict volocity
    def predict(self,rudder,sail):
        self.rudder=rudder
        self.sail=sail
        '''predict angle'''
        self.angular_volocity+=3*(rudder-85)*self.sample_time
        if self.angular_volocity>0:
            self.angular_volocity-=self.angular_volocity**2*self.sample_time/2.5
        elif self.angular_volocity<0:
            self.angular_volocity+=self.angular_volocity**2*self.sample_time/2.5
        self.volocity[1]+=self.angular_volocity

        """#predict speed"""

        if self.volocity[1]<90 and self.volocity[1]>-45:
            if self.sail==1:
                self.volocity[0]+=(55-self.volocity[1])**1/3*self.sample_time
        elif self.volocity[1]>=90:
            if self.sail==1:
                self.volocity[0]+=(self.volocity[1]-125)**1/3*self.sample_time
        elif self.volocity[1]<=-135:
            if self.sail==1:
                self.volocity[0]+=(self.volocity[1]+235)**1/3*self.sample_time
        else:
            if self.sail==1:
                self.volocity[0]+=abs(2*self.volocity[1]+180)**1/3*self.sample_time
        
        self.volocity[0]-=(abs(rudder-85)**1/3+(self.volocity[0]**2)/300)*self.sample_time


        if self.volocity[1]>180:
            self.volocity[1]-=360
        elif self.volocity[1]<-180:
            self.volocity[1]+=360
        if self.volocity[0]<0:
            if self.volocity[1]>=0:
                self.volocity[1]-=180
            else:
                self.volocity[1]+=180
            self.volocity[0]=-self.volocity[0]
        '''predict loacation'''
        self.location[0]+=self.volocity[0]*math.cos(self.volocity[1]/57.32)*self.sample_time
        self.location[1]+=self.volocity[0]*math.sin(self.volocity[1]/57.32)*self.sample_time-self.location[1]**0.8*0.03*self.sample_time



        return self.location, self.volocity
            






        
        





                