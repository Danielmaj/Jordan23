import pyrealsense2 as rs
import numpy as np
import cv2
import sys
sys.path.append('../')
from Image_Processing.Image_Handler import Image_Handler
from Hardware.mainboard import *
from Hardware.Motor import *
from config import Config
from time import sleep

def LocateBasket(frame,color,config):

    if color == "blue":
        low = config.lower_blue
        up = config.upper_blue
    else:
        low = config.lower_magenta
        up = config.upper_magenta


    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, low, up)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=1)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    if len(cnts) > 0:

        c = max(cnts, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        print("x",x,"y", y,"w", w,"h", h)
        # only proceed if the basket meets a minimum size
        if w*h > 20:
            center = (int(x), int(y))
    return center


def Start_Pipeline(config):

    # Configure depth and color streams
    pipeline = rs.pipeline()
    rsconfig = rs.config()
    rsconfig.enable_stream(rs.stream.depth, config.frame_width, config.frame_heigth, rs.format.z16, 60)
    rsconfig.enable_stream(rs.stream.color, config.frame_width, config.frame_heigth, rs.format.bgr8, 60)
    # Start streaming
    pipeline.start(rsconfig)

    return pipeline

def Get_frames(pipeline):
    # Wait for a coherent pair of frames: depth and color
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue
        else:
            break
    return color_frame,depth_frame


def Rotate_towards(obj_name,com,coordinates,config):
    x,y = coordinates
    centred = False
    if x > config.max_cent_x:
       move(com,right(config.cent_vel))
    elif x < config.min_cent_x:
       move(com,left(config.cent_vel))
    else:
       print('Centered on:',obj_name)
       move(com,stop())
       centred = True
    return centred


def Where_is(obj_name,color_frame,img_handler,config):

    coordinates = None
    color_image = np.asanyarray(color_frame.get_data())

    if obj_name == 'ball':
        coordinates = img_handler.LocateBallCenter(color_image)
    else:
        coordinates = LocateBasket(color_image,"blue",config)

    return coordinates


def CenterOn(obj_name,com,pipeline,img_handler,config):

    centered = False

    rotate = 0
    while not centered:

        color_frame,depth_frame = Get_frames(pipeline)
        coordinates = Where_is(obj_name,color_frame,img_handler,config)

        if coordinates == None:
            rotate+=1
            if rotate < config.rot_wait:
                move(com,left(config.rot_vel))
                time.sleep(config.wait_time)
                rotate = 0
        else:
            print("Coordinates",coordinates)
            centered = Rotate_towards(obj_name,com,coordinates,config)


def GoTowards(obj_name,com,pipeline,img_handler,config,until,vel):

    near = False
    while not near:

        color_frame,depth_frame = Get_frames(pipeline)
        coordinates = Where_is(obj_name,color_frame,img_handler,config)

        if coordinates == None:
            CenterOn(obj_name,com,pipeline,img_handler,config)
        else:
            x,y = coordinates
            dist = depth_frame.get_distance(int(x),int(y))
            if dist > until:
                move(com,wheelspeeds(vel,90,0))
            elif dist > 0.1:
                near = True
                move(com,stop())
            time.sleep(config.wait_time)


def ang_vel_towards(obj_name,com,coordinates,config):
    x,y = coordinates
    if x > config.max_cent_x:
       ang_vel = around_ang_vel
    elif x < config.min_cent_x:
       ang_vel = - around_ang_vel
    else:
       print('Centered on:',obj_name)
    return ang_vel


def Aling_Basket_Ball(com,pipeline,img_handler,config):
    #Todo add constants to config
    align = False

    while not align:

        color_frame,depth_frame = Get_frames(pipeline)
        coordinates_basket = Where_is("basket",color_frame,img_handler,config)
        coordinates_ball = Where_is("ball",color_frame,img_handler,config)

        if coordinates_ball == None:
            CenterOn('ball',com,pipeline,img_handler,config)

        else:

            xb,yb = coordinates_ball

            if xb > config.max_cent_x:
               ang_vel = -config.around_ang_vel
            elif xb < config.min_cent_x:
               ang_vel = config.around_ang_vel
            else:
               ang_vel = 0

            if coordinates_basket == None:

                move(com,wheelspeeds(10,180,ang_vel))
                time.sleep(config.wait_time)

            else:

                xk,yk = coordinates_basket

                if xk > config.max_bask_x:
                    print("right")
                    print(ang_vel)
                    move(com,wheelspeeds(5,0,ang_vel))
                elif xk < config.min_bask_x:
                    print("left")
                    print(ang_vel)
                    move(com,wheelspeeds(5,180,ang_vel))
                else:
                   move(com,stop())
                   align = True
                   print("Basket x",xk)
                   print("Ball x",xb)

                time.sleep(config.wait_time)


def main():

    com = ComportMainboard()
    com.open()

    config = Config()
    pipeline = Start_Pipeline(config)
    img_handler = Image_Handler()

    steps_forward = 50

    for i in range(steps_forward):
        move(com,wheelspeeds(15,90,0))
        time.sleep(config.wait_time)

    CenterOn('ball',com,pipeline,img_handler,config)

    GoTowards('ball',com,pipeline,img_handler,config,until=0.4,vel=15)

    Aling_Basket_Ball(com,pipeline,img_handler,config)

    #GoTowards('ball',com,pipeline,img_handler,config,until=0.2,vel=5)

    #Launch the ball
    #Launch the ball
    #com.launch_motor(2000)

    pipeline.stop()
    com.close()

main()
