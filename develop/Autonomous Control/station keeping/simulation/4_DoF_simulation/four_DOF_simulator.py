import math
import numpy as np 
import numpy.linalg as lg

''' zs=0.4,sail length=0.3, distance from sail to the center=0.05 
    m=2
'''
# class four_DOF_simulator():
#     def __init__(self,sample_time=0.01):
#         self.sample_time=sample_time
#         self.velocity=np.array([0,0,0]).T

#         self.angular_velocity=[0,0,0]
#         self.v_and_angular_v=[0,0,0,0]
#         self.sail=0
#         self.rudder=0


def to_next_moment(sample_time,u,v,p,r,x,y,roll,yaw,sail,rudder,true_wind):  ##true_wind[vx,vy]
    
    velocity,angular_velocity,v_and_angular_v,location_and_orientation=get_all_parameters(u,v,p,r,x,y,roll,yaw)
    app_wind_speed,angle_app_wind,wind_angle_of_attack=get_app_wind(true_wind,velocity,angular_velocity,roll,yaw,u,v,r,p,sail)
    sail_torque=get_sail_torque(sail,wind_angle_of_attack,app_wind_speed,angle_app_wind)
    # print(sail_torque)
    rudder_torque=get_rudder_torque(rudder,u,v,r,p)
    Mass_and_inertia_matrix_inverse=get_M()
    # print(Mass_and_inertia_matrix_inverse.dtype)
    Coriolis_v=get_C_v(u,v,p,r)
    D_vn=get_D_vn(u,v,p,r,roll,yaw)
    g_n=get_g_n(roll)
    j_n=get_j_n(yaw,roll)
    all_other_terms=-Coriolis_v.dot(v_and_angular_v)-D_vn-g_n+sail_torque+rudder_torque
    # print('C',Coriolis_v.dot(v_and_angular_v),'\nD',D_vn,'\ng',g_n,'\nrudder tor',rudder_torque,rudder)
    # print('sail tor',sail_torque)
    # print('C',Coriolis_v.dot(v_and_angular_v))
    # print('rudder tor',rudder_torque)
    # print('D',-D_vn)
    # print('all term',Mass_and_inertia_matrix_inverse.dot(all_other_terms))
    v_and_angular_v=v_and_angular_v.astype(np.float64)
    location_and_orientation=location_and_orientation.astype(np.float64)
    # print(v_and_angular_v.dtype)
    # print('v and n',v_and_angular_v,location_and_orientation)
    v_and_angular_v+=Mass_and_inertia_matrix_inverse.dot(all_other_terms)*sample_time
    # print(location_and_orientation,'\n',j_n,j_n.dot(v_and_angular_v)*sample_time,'aaa')
    # print(location_and_orientation)
    location_and_orientation+=j_n.dot(v_and_angular_v)*sample_time
    # print('v and n',v_and_angular_v,location_and_orientation)
    return v_and_angular_v,location_and_orientation,angle_app_wind

    
def get_all_parameters(u,v,p,r,x,y,roll,yaw):
    velocity=np.array([u,v,0]).T
    angular_velocity=np.array([p,0,r]).T
    v_and_angular_v=np.array([u,v,p,r]).T
    location_and_orientation=np.array([x,y,roll,yaw]).T
    # print(location_and_orientation)
    return velocity,angular_velocity,v_and_angular_v,location_and_orientation

def get_app_wind(true_wind,velocity,angular_velocity,roll,yaw,u,v,r,p,sail):
    # true_wind_n_frame=np.array([true_wind[0]*math.cos(true_wind[1]),true_wind[0]*math.sin(true_wind[1]),0]).T
    # R1=np.array([[math.cos(-yaw),math.sin(-yaw),0],
    #             [math.sin(-yaw),math.cos(-yaw),0],
    #             [0             ,0             ,1]])

    # R2=np.array([[1            ,0             ,0],
    #             [0,math.cos(-roll),math.sin(-roll)],
    #             [0,math.sin(-roll),math.cos(-roll)]])
    
    # transform_matrix=R1.dot(R2)
    # true_wind_b_frame=true_wind_n_frame.dot(transform_matrix)
    ys=0.1
    app_wind_on_u=true_wind[0]*math.cos(true_wind[1]-yaw)-u+r*(0.15*math.cos(sail)-0.05)
    app_wind_on_v=true_wind[0]*math.sin(true_wind[1]-yaw)*math.cos(roll)-v-r*0.15*math.sin(sail)+p*0.4
    # print(true_wind[0]*math.cos(true_wind[1]-yaw),u,r*(0.15*math.cos(sail)-0.05))
    
    v_app_wind=math.sqrt(app_wind_on_v**2+app_wind_on_u**2)
    angle_app_wind=math.atan2(app_wind_on_v,-app_wind_on_u)
    # print(app_wind_on_u,app_wind_on_v,'app wind',angle_app_wind)
    wind_angle_of_attack=angle_app_wind-sail
    return v_app_wind,angle_app_wind,wind_angle_of_attack
    
def get_sail_torque(sail,wind_angle_of_attack,app_wind_speed,angle_app_wind):
    sail_lift=0.5*1.29*0.1*app_wind_speed**2*4*lift_coefficients(wind_angle_of_attack)  ##0.5*density*A*v^2*4=2.5
    sail_drag=0.5*1.29*0.1*app_wind_speed**2*4*drag_coefficients(wind_angle_of_attack)  #Ds
    # print('lift',sail_lift,'drag',sail_drag,'attack angle',wind_angle_of_attack)
    sail_torque=np.array([sail_lift*math.sin(angle_app_wind)-sail_drag*math.cos(angle_app_wind),
                        sail_lift*math.cos(angle_app_wind)+sail_drag*math.sin(angle_app_wind),
                        (sail_lift*math.cos(angle_app_wind)+sail_drag*math.sin(angle_app_wind))*0.4,
                        -(sail_lift*math.sin(angle_app_wind)-sail_drag*math.cos(angle_app_wind))*0.1*math.sin(sail)
                        +(sail_lift*math.cos(angle_app_wind)+sail_drag*math.sin(angle_app_wind))*(0.1*math.cos(sail))])
    sail_torque=sail_torque.T
    # print('sail tor',sail_torque,wind_angle_of_attack)
    # print('app wind',[app_wind_speed,angle_app_wind])
    return sail_torque

def lift_coefficients(angle_of_attack):
    if math.cos(angle_of_attack)>-0.9:
        lift_coefficient=math.sin(2*angle_of_attack)
    else:
        lift_coefficient=0
    return lift_coefficient

def drag_coefficients(angle_of_attack):
    if math.cos(angle_of_attack)>-0.9:
        drag_coefficient=0.75-0.68*math.cos((2*angle_of_attack))
    else:
        drag_coefficient=0.75
    return drag_coefficient

def get_rudder_torque(rudder,u,v,r,p):
    u_rudder=-u+r*0 #yr=0
    v_rudder=-v-r*0.3+p*-0.1 #xr=0.3,zr=-0.15
    # print(-v,-r*0.3,-p*0.1)

    rudder_speed=math.sqrt(v_rudder**2+u_rudder**2)
    angle_app_rudder=math.atan2(v_rudder,-u_rudder)
    rudder_angle_of_attack=angle_app_rudder-rudder
    
    rudder_lift=7*rudder_speed**2*lift_coefficients(rudder_angle_of_attack)
    rudder_drag=5*rudder_speed**2*drag_coefficients(rudder_angle_of_attack)
    # print('rudder',rudder,'speed',rudder_speed,'angle',rudder_angle_of_attack,"L",rudder_lift,"d",rudder_drag)
    rudder_torque=np.array([rudder_lift*math.sin(angle_app_rudder)-rudder_drag*math.cos(angle_app_rudder),
                            rudder_lift*math.cos(angle_app_rudder)+rudder_drag*math.sin(angle_app_rudder),
                            -(rudder_lift*math.cos(angle_app_rudder)+rudder_drag*math.sin(angle_app_rudder))*0.1,
                            -(rudder_lift*math.cos(angle_app_rudder)+rudder_drag*math.sin(angle_app_rudder))*0.35])
    
    rudder_torque=rudder_torque.T
    # print('rudder tor',rudder_torque,[rudder_speed,rudder_angle_of_attack],angle_app_rudder,[rudder_lift,rudder_drag])
    return rudder_torque

def get_M():
    M=np.array([[3,0.0,0.0,0.0],
                [0.0,15,0.0,0.0],
                [0.0,0.0,0.3,0.0],
                [0.0,0.0,0.0,0.8]])
    M_inv=lg.inv(M)
    return M_inv

def get_C_v(u,v,p,r):
    C_v=np.array([[0,-2*r,0,2*v],
                [2*r,0,0,-2*u],
                [0,0,0,0],
                [-2*v,2*u,0,0]])
    return C_v

def get_D_vn(u,v,p,r,roll,yaw):
    D_heel_and_yaw=np.array([0,0,2*abs(p)*p,1.1*abs(r)*r*math.cos(roll)]).T
    # print("D_heel_and_yaw",-D_heel_and_yaw)
    D_k=get_D_k(u,v,p,r,roll,yaw)
    D_h=get_D_h(u,v,p,r,roll,yaw)
    
    D_vn=D_heel_and_yaw+D_h+D_k
    return D_vn

def get_D_k(u,v,p,r,roll,yaw):
    keel_u=-u
    keel_v=-v+p*0.15-r*0.1
    keel_speed=math.sqrt(keel_u**2+keel_v**2)
    keel_angle_of_attack=math.atan2(keel_v,-keel_u)
    keel_lift=8*keel_speed**2*lift_coefficients(keel_angle_of_attack)
    keel_drag=8*keel_speed**2*drag_coefficients(keel_angle_of_attack)
    D_k=np.array([-keel_lift*math.sin(keel_angle_of_attack)+keel_drag*math.cos(keel_angle_of_attack),
                -keel_lift*math.cos(keel_angle_of_attack)-keel_drag*math.sin(keel_angle_of_attack),
                (-keel_lift*math.cos(keel_angle_of_attack)-keel_drag*math.sin(keel_angle_of_attack))*0.1,
                (keel_lift*math.cos(keel_angle_of_attack)+keel_drag*math.sin(keel_angle_of_attack))*0.03])
    D_k=D_k.T 
    # print('Dk',-D_k,keel_speed,keel_angle_of_attack)
    return D_k

def get_D_h(u,v,p,r,roll,yaw):
    hull_u=-u
    try:
        hull_v=-v-0.15*r/math.cos(roll)
    except:
        print('error! abnormal roll')
    hull_speed=math.sqrt(hull_u**2+hull_v**2)
    hull_angle_of_attack=math.atan2(hull_v,-hull_u)
    F_rh=16*hull_speed**2*drag_coefficients(hull_angle_of_attack)
    h_lift=16*hull_speed**2*lift_coefficients(hull_angle_of_attack)
    D_h=np.array([-h_lift*math.sin(hull_angle_of_attack)+F_rh*math.cos(hull_angle_of_attack),
                -h_lift*math.cos(hull_angle_of_attack)-F_rh*math.sin(hull_angle_of_attack)*math.cos(roll),
                (-h_lift*math.cos(hull_angle_of_attack)-F_rh*math.sin(hull_angle_of_attack))*math.cos(roll)*0.03,
                (-h_lift*math.cos(hull_angle_of_attack)-F_rh*math.sin(hull_angle_of_attack))*math.cos(roll)*0.02])
    # print('Dh',-D_h,hull_angle_of_attack)
    return D_h.T
    
def get_g_n(roll):
    g_n=np.array([0,0,(0.8*roll**2+0.5*abs(roll))*sign(roll),0]).T
    # print('gn',-g_n)
    return g_n

def get_j_n(yaw,roll):
    j_n=np.array([[math.cos(yaw),-math.sin(yaw)*math.cos(roll),0,0],
                [math.sin(yaw),math.cos(yaw)*math.cos(roll),0,0],
                [0,0,1,0],
                [0,0,0,math.cos(roll)]])
    # print(yaw,roll)
    return j_n

def sign(p):
    if p>0:
        return 1
    elif p<0:
        return -1
    else:
        return 0