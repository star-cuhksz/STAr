import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import time
import math
import threading
from sailboat_for_simulation_pid_v2 import sailboat
import random


class visualazation():
    def __init__(self):
        self.start_time=time.time()
        self.my_boat=sailboat()
        self.x=self.my_boat.location[0]
        self.y=self.my_boat.location[1]
        self.heading_angle=self.my_boat.heading_angle
        self.desired_angle=self.my_boat.desired_angle
        self.rudder=self.my_boat.rudder
        self.sail=self.my_boat.sail
        self.v=self.my_boat.velocity[0]
        self.u=self.my_boat.velocity[1]
        self.w=self.my_boat.angular_velocity
        self.target=self.my_boat.target


        self.figure = plt.figure()
        self.gs1 = gridspec.GridSpec(1, 1)
        self.gs2 = gridspec.GridSpec(3, 1)

        self.main_window=self.figure.add_subplot(self.gs1[0])
        ##this part is for target area and pre-arrive area.
        theta = np.linspace(0, 2*np.pi,100)
        x_t,y_t = np.cos(theta)*5+np.linspace(self.my_boat.target[0],self.my_boat.target[0],100), np.sin(theta)*5+np.linspace(self.my_boat.target[1],self.my_boat.target[1],100)
        self.main_window.plot(x_t, y_t, color='red', linewidth=1.0)
        
        x_p,y_p = np.cos(theta)*10+np.linspace(self.my_boat.target[0],self.my_boat.target[0],100), np.sin(theta)*10+np.linspace(self.my_boat.target[1],self.my_boat.target[1],100)
        self.main_window.plot(x_p, y_p, color='orange', linewidth=1.0)


        self.main_window.axis('equal')

        plt.xlim(-5,42)
        plt.ylim(-5,55)
        self.gs1.tight_layout(self.figure, rect=[0, 0, 0.7, 1])

        self.forward_velocity_window = self.figure.add_subplot(self.gs2[0])
        plt.xlabel('forward velocity')
        plt.ylim(-0.5,5)
        self.side_velocity_window = self.figure.add_subplot(self.gs2[1])
        plt.xlabel('side velocity')
        plt.ylim(-0.2,0.2)
        self.angular_velocity_window = self.figure.add_subplot(self.gs2[2])
        plt.xlabel('angular velocity')
        plt.ylim(-1,1)
        self.gs2.tight_layout(self.figure, rect=[0.7, 0, 1, 1], h_pad=0.5)



        top = min(self.gs1.top, self.gs2.top)
        bottom = max(self.gs1.bottom, self.gs2.bottom)

        self.gs1.update(top=top, bottom=bottom)
        self.gs2.update(top=top, bottom=bottom)


        self.location_x_data = np.linspace(self.my_boat.location[0],self.my_boat.location[0],2000)
        self.location_y_data=np.linspace(self.my_boat.location[1],self.my_boat.location[1],2000)
        self.trajectory_line, = self.main_window.plot(self.location_x_data,self.location_y_data)
        self.v_x_data = np.linspace(0, 5, 500)
        self.v_data=np.linspace(self.v,self.v,500)
        self.line_forward_velocity, = self.forward_velocity_window.plot(self.v_x_data, self.v_data)
        # x2_data = np.linspace(0, 5, 500)
        self.u_data=np.linspace(self.u,self.u,500)
        self.line_side_velocity, = self.side_velocity_window.plot(self.v_x_data, self.u_data)
        # x3_data = np.linspace(0, 5, 500)
        self.w_data=np.linspace(self.w,self.w,500)
        self.line_angular_velocity, = self.angular_velocity_window.plot(self.v_x_data, self.w_data)
        self.boat_y_data=np.array([-math.sin(self.heading_angle)-math.cos(self.heading_angle)*0.5,
                            math.sin(self.heading_angle)-math.cos(self.heading_angle)*0.5,
                            1.5*math.sin(self.heading_angle),
                            math.sin(self.heading_angle)+math.cos(self.heading_angle)*0.5,
                            -math.sin(self.heading_angle)+math.cos(self.heading_angle)*0.5])
        self.boat_x_data=np.array([-math.cos(self.heading_angle)+math.sin(self.heading_angle)*0.5,
                            math.cos(self.heading_angle)+math.sin(self.heading_angle)*0.5,
                            1.5*math.cos(self.heading_angle),
                            math.cos(self.heading_angle)-math.sin(self.heading_angle)*0.5,
                            -math.cos(self.heading_angle)-math.sin(self.heading_angle)*0.5])
        self.line_boat, = self.main_window.plot(self.boat_x_data+np.linspace(self.x,self.x,5),self.boat_y_data+np.linspace(self.y,self.y,5))

        self.rudder_y_data=np.array([-math.sin(self.heading_angle),
                                -math.sin(self.heading_angle)-math.cos(self.rudder-math.pi/2+self.heading_angle)])
        self.rudder_x_data=np.array([-math.cos(self.heading_angle),
                                -math.cos(self.heading_angle)+math.sin(self.rudder-math.pi/2+self.heading_angle)])
        self.line_rudder,=self.main_window.plot(self.rudder_x_data+np.linspace(self.x,self.x,2),self.rudder_y_data+np.linspace(self.y,self.y,2))

        self.sail_y_data=np.array([0.8*math.sin(self.heading_angle),
                                0.8*math.sin(self.heading_angle)-2*math.cos(self.sail-math.pi/2+self.heading_angle)])
        self.sail_x_data=np.array([0.8*math.cos(self.heading_angle),
                                0.8*math.cos(self.heading_angle)+2*math.sin(self.sail-math.pi/2+self.heading_angle)])
        self.line_sail,=self.main_window.plot(self.sail_x_data+np.linspace(self.x,self.x,2),self.sail_y_data+np.linspace(self.x,self.x,2))

        self.window_y_data=np.array([-5,15,15,15,30,30])
        self.window_x_data=np.array([27,27,42,27,27,42])
        self.line_window,=self.main_window.plot(self.window_x_data,self.window_y_data,color='b')

        self.window_boat_y_data=5*self.boat_y_data+np.linspace(5,5,5)
        self.window_boat_x_data=5*self.boat_x_data+np.linspace(34.5,34.5,5)
        self.line_win_boat,=self.main_window.plot(self.window_boat_x_data,self.window_boat_y_data)

        self.window_rudder_y_data=3*self.rudder_y_data+np.linspace(5,5,2)
        self.window_rudder_x_data=3*self.rudder_x_data+np.linspace(34.5,34.5,2)
        self.line_win_rudder,=self.main_window.plot(self.window_rudder_x_data,self.window_rudder_y_data)

        self.window_sail_y_data=4*self.sail_y_data+np.linspace(5,5,2)
        self.window_sail_x_data=4*self.sail_x_data+np.linspace(34.5,34.5,2)
        self.line_win_sail,=self.main_window.plot(self.window_sail_x_data,self.window_sail_y_data)


        self.wind_y_data=np.array([22.5,30])
        self.wind_x_data=np.array([34.5,34.5])
        self.line_wind,=self.main_window.plot(self.wind_x_data,self.wind_y_data)

        self.line_disired_angle,=self.main_window.plot([1.5*math.cos(self.heading_angle),1.5*math.cos(self.heading_angle)+math.cos(self.desired_angle)],
                                    [1.5*math.sin(self.heading_angle),1.5*math.sin(self.heading_angle)+math.sin(self.desired_angle)])

        Y, X = np.mgrid[-5:42:6j, -5:50:6j]
        I=np.ones_like(Y)
        

    def init1(self):  # only required for blitting to give a clean slate.
        
        return self.trajectory_line,self.line_forward_velocity,self.line_side_velocity,self.line_angular_velocity,self.line_boat,self.line_rudder,self.line_sail,self.line_win_boat,self.line_win_rudder,self.line_win_sail,self.line_wind,self.line_disired_angle,


    def animate1(self,i):
        # global self.v_data,self.v_x_data,self.location_x_data,self.location_y_data,self.u_data,self.w_data,self.x,self.y,self.heading_angle,self.desired_angle
        # global self.boat_x_data,self.boat_y_data,Y,X
        # ,self.rudder_x_data,self.rudder_y_data
        info=self.my_boat.to_next_moment()
        info=self.my_boat.to_next_moment()
        info=self.my_boat.to_next_moment()
        info=self.my_boat.to_next_moment()
        info=self.my_boat.to_next_moment()
        info=self.my_boat.to_next_moment()
        info=self.my_boat.to_next_moment()
        info=self.my_boat.to_next_moment()
        
        self.x=info[0][0]
        self.y=info[0][1]
        self.rudder=info[1]
        self.sail=info[2]
        
        self.desired_angle=info[3]
        self.heading_angle=info[4]
        self.w=self.my_boat.angular_velocity
        self.v=self.my_boat.velocity[0]
        
        self.u=self.my_boat.velocity[1]
        # print(self.v,u)
        self.location_x_data=np.delete(self.location_x_data,0,0)
        self.location_x_data=np.append(self.location_x_data,[self.x],0)
        self.location_y_data=np.delete(self.location_y_data,0,0)
        self.location_y_data=np.append(self.location_y_data,[self.y],0)
        self.trajectory_line.set_data(self.location_x_data,self.location_y_data)

        self.v_data=np.delete(self.v_data,0,0)
        self.v_data=np.append(self.v_data,[self.v],0)
        self.line_forward_velocity.set_ydata(self.v_data)  # update the data.

        
        self.u_data=np.delete(self.u_data,0,0)
        self.u_data=np.append(self.u_data,[self.u],0)
        self.line_side_velocity.set_ydata(self.u_data)  # update the data.
        self.w_data=np.delete(self.w_data,0,0)
        self.w_data=np.append(self.w_data,[self.w],0)
        self.line_angular_velocity.set_ydata(self.w_data)


        self.boat_y_data=np.array([-math.sin(self.heading_angle)-math.cos(self.heading_angle)*0.5,
                            math.sin(self.heading_angle)-math.cos(self.heading_angle)*0.5,
                            1.5*math.sin(self.heading_angle),
                            math.sin(self.heading_angle)+math.cos(self.heading_angle)*0.5,
                            -math.sin(self.heading_angle)+math.cos(self.heading_angle)*0.5])
        self.boat_x_data=np.array([-math.cos(self.heading_angle)+math.sin(self.heading_angle)*0.5,
                            math.cos(self.heading_angle)+math.sin(self.heading_angle)*0.5,
                            1.5*math.cos(self.heading_angle),
                            math.cos(self.heading_angle)-math.sin(self.heading_angle)*0.5,
                            -math.cos(self.heading_angle)-math.sin(self.heading_angle)*0.5])

        if self.my_boat.if_acc==1:
            
            self.line_boat, = self.main_window.plot(self.boat_x_data+np.linspace(self.x,self.x,5),self.boat_y_data+np.linspace(self.y,self.y,5),color='r')
        elif self.my_boat.if_acc==0:
            self.line_boat, = self.main_window.plot(self.boat_x_data+np.linspace(self.x,self.x,5),self.boat_y_data+np.linspace(self.y,self.y,5),color='black')
        

        self.rudder_y_data=np.array([-math.sin(self.heading_angle),
                                -math.sin(self.heading_angle)-math.cos(self.rudder-math.pi/2+self.heading_angle)])
        self.rudder_x_data=np.array([-math.cos(self.heading_angle),
                                -math.cos(self.heading_angle)+math.sin(self.rudder-math.pi/2+self.heading_angle)])
        self.line_rudder,=self.main_window.plot(self.rudder_x_data+np.linspace(self.x,self.x,2),self.rudder_y_data+np.linspace(self.y,self.y,2),color='blue')

        self.sail_y_data=np.array([0.8*math.sin(self.heading_angle),
                                0.8*math.sin(self.heading_angle)-2*math.cos(self.sail-math.pi/2+self.heading_angle)])
        self.sail_x_data=np.array([0.8*math.cos(self.heading_angle),
                                0.8*math.cos(self.heading_angle)+2*math.sin(self.sail-math.pi/2+self.heading_angle)])
        self.line_sail,=self.main_window.plot(self.sail_x_data+np.linspace(self.x,self.x,2),self.sail_y_data+np.linspace(self.y,self.y,2),color='blue')

        

        self.window_boat_y_data=5*self.boat_y_data+np.linspace(5,5,5)
        self.window_boat_x_data=5*self.boat_x_data+np.linspace(34.5,34.5,5)
        self.line_win_boat,=self.main_window.plot(self.window_boat_x_data,self.window_boat_y_data,color='black')

        self.window_rudder_y_data=3*self.rudder_y_data+np.linspace(5,5,2)
        self.window_rudder_x_data=3*self.rudder_x_data+np.linspace(34.5,34.5,2)
        self.line_win_rudder,=self.main_window.plot(self.window_rudder_x_data,self.window_rudder_y_data,color='blue')

        self.window_sail_y_data=4*self.sail_y_data+np.linspace(5,5,2)
        self.window_sail_x_data=4*self.sail_x_data+np.linspace(34.5,34.5,2)
        self.line_win_sail,=self.main_window.plot(self.window_sail_x_data,self.window_sail_y_data,color='blue')


        coo_wind=self.my_boat.get_true_wind()[1]
        del_x=coo_wind[0]/2
        del_y=coo_wind[1]/2
        self.wind_y_data=np.array([22.5,del_y+22.5])
        self.wind_x_data=np.array([34.5,del_x+34.5])
        self.line_wind,=self.main_window.plot(self.wind_x_data,self.wind_y_data,color='black')

        self.line_disired_angle,=self.main_window.plot([1.5*math.cos(self.heading_angle)+self.x,1.5*math.cos(self.heading_angle)+math.cos(self.desired_angle)+self.x],
                                    [1.5*math.sin(self.heading_angle)+self.y,1.5*math.sin(self.heading_angle)+math.sin(self.desired_angle)+self.y],color='gray')



        # t=self.my_boat.time
        # V = 1*I+0.5*math.sin(math.sin(6.28*t)/12*math.pi+math.pi/2)*I
        # U = 0.5*math.cos(math.sin(6.28*t)/12*math.pi-math.pi/2)*I

        # Y1,X1=(Y+V).flatten(),(X+U).flatten()
        # Y0,X0=Y.flatten(),X.flatten()
        # line_winds=[]
        # for i in range(0,36):
            
        #     self.location_x_data=np.hstack((X0[i],X1[i]))
        #     self.location_y_data=np.hstack((Y0[i],Y1[i]))
            
        #     # self.trajectory_line.set_data(self.location_x_data,self.location_y_data)
        #     # print(self.location_x_data,self.location_y_data)
        #     self.line_wind,=self.main_window.plot(self.location_x_data,self.location_y_data,color='gray')
        #     # yield self.line_wind
        #     line_winds.append(self.line_wind)

        return self.trajectory_line,self.line_forward_velocity,self.line_side_velocity,self.line_angular_velocity,self.line_boat,self.line_rudder,self.line_sail,self.line_win_boat,self.line_win_sail,self.line_win_rudder,self.line_wind,self.line_disired_angle,









    # def init_boat():  # only required for blitting to give a clean slate.
        
    #     return self.line_boat,

    # def animate_boat(i):
    #     global self.boat_y_data,self.boat_x_data,self.x,self.y
        
    def plot(self):
        ani = animation.FuncAnimation(
            self.figure, self.animate1, init_func=self.init1, interval=5, blit=True, save_count=50)
        # ani_boat = animation.FuncAnimation(
        #     self.figure, animate_boat, init_func=init_boat, interval=5, blit=True, save_count=50)
        # To save the animation, use e.g.
        #
        # ani.save("movie.mp4")
        #
        # or
        #
        # from matplotlib.animation import FFMpegWriter
        # writer = FFMpegWriter(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        # ani.save("movie.mp4", writer=writer)

        plt.show()
    
