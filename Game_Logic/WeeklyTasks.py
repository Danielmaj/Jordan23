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
import json

DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07"]
def find_device_that_supports_advanced_mode() :
    ctx = rs.context()
    ds5_dev = rs.device()
    devices = ctx.query_devices();
    for dev in devices:
        if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DS5_product_ids:
            if dev.supports(rs.camera_info.name):
                print("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name))
            return dev
    raise Exception("No device that supports advanced mode was found")

def Start_Pipeline(config):

    # Configure depth and color streams
    pipeline = rs.pipeline()
    rsconfig = rs.config()
    rsconfig.enable_stream(rs.stream.depth, config.frame_width, config.frame_heigth, rs.format.z16, 60)
    rsconfig.enable_stream(rs.stream.color, config.frame_width, config.frame_heigth, rs.format.bgr8, 60)
    # Start streaming
    pipeline.start(rsconfig)
    try:
        dev = find_device_that_supports_advanced_mode()
        advnc_mode = rs.rs400_advanced_mode(dev)
        print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")

        # Loop until we successfully enable advanced mode
        while not advnc_mode.is_enabled():
            print("Trying to enable advanced mode...")
            advnc_mode.toggle_advanced_mode(True)
            # At this point the device will disconnect and re-connect.
            print("Sleeping for 5 seconds...")
            time.sleep(5)
            # The 'dev' object will become invalid and we need to initialize it again
            dev = find_device_that_supports_advanced_mode()
            advnc_mode = rs.rs400_advanced_mode(dev)
            print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")

        # Serialize all controls to a Json string
        serialized_string = advnc_mode.serialize_json()
        as_json_object = json.loads(serialized_string)

        # We can also load controls from a json string
        # For Python 2, the values in 'as_json_object' dict need to be converted from unicode object to utf-8
        if type(next(iter(as_json_object))) != str:
            as_json_object = {k.encode('utf-8'): v.encode("utf-8") for k, v in as_json_object.items()}
            
        #Set auto white balance to False
        as_json_object['controls-color-white-balance-auto'] = 'False'
        as_json_object['controls-color-autoexposure-auto']='False'
        as_json_object['controls-autoexposure-auto']= 'False' 
        
        # The C++ JSON parser requires double-quotes for the json object so we need
        # to replace the single quote of the pythonic json to double-quotes
        json_string = str(as_json_object).replace("'", '\"')
        advnc_mode.load_json(json_string)

    except Exception as e:
        print(e)
    ## Skip first 2 seconds frames
    #print('Skipping frames')
    #for i in range(120):
    #    frames = pipeline.wait_for_frames()
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
       move(com,left(config.cent_vel))
    elif x < config.min_cent_x:
       move(com,right(config.cent_vel))
    else:
       print('Centered on:',obj_name)
       move(com,stop())
       centred = True
    return centred


def Where_is(obj_name,color_frame,img_handler,config):
    global My_ID
    coordinates = None
    color_image = np.asanyarray(color_frame.get_data())

    if obj_name == 'ball':
        coordinates = img_handler.LocateBallCenter(color_image)
    else:
        #coordinates = img_handler.LocateBasket(color_image,"blue",config)
        if My_ID =='A':
            coordinates = img_handler.LocateBasket(color_image,"blue",config)
        else:
            coordinates = img_handler.LocateBasket(color_image,"redl",config)

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
            print(dist)
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
    ball_align = False

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
               ball_align = False
            elif xb < config.min_cent_x:
               ang_vel = config.around_ang_vel
               ball_align = False
            else:
               ball_align = True
               ang_vel = 0

            if coordinates_basket == None:

                move(com,wheelspeeds(10,0,ang_vel))
                time.sleep(config.wait_time)

            else:

                xk,yk = coordinates_basket

                if xk > config.max_bask_x:
                    print("right")
                    print(ang_vel)
                    move(com,wheelspeeds(7,180,ang_vel))
                elif xk < config.min_bask_x:
                    print("left")
                    print(ang_vel)
                    move(com,wheelspeeds(7,0,ang_vel))
                else:
                    if ball_align:
                        move(com,stop())
                        align = True
                        print("Basket x",xk)
                        print("Ball x",xb)
                        bas_dist = depth_frame.get_distance(xk,yk)
                        ball_dist = depth_frame.get_distance(xb,yb)
			t_dist = bas_dist - ball_dist
			print('dist:{}'.format(t_dist))
                        CalculateThrowerStrength(t_dist)
                    else:

                        move(com,wheelspeeds(0,0,ang_vel))
                        print("aligning with ball",ang_vel)

                time.sleep(config.wait_time)

Thrower_Strength = -1
def CalculateThrowerStrength(dist):
    global Thrower_Strength
    #Thrower_Strength=int(14.558*dist + 158)
    #val = 14.558*dist + 158
    Thrower_Strength= 10*pow(dist,2)-19*dist + 194
    print('poly:{}'.format(Thrower_Strength))
    Thrower_Strength = int(Thrower_Strength)

def main():
    global Thrower_Strength

    global Myfield 
    Myfield ='A'
    global My_ID
    My_ID = 'A'
    com = ComportMainboard()
    com.open()
    config = Config()
    pipeline = Start_Pipeline(config)
    img_handler = Image_Handler()
    steps_forward = 5
    com.in_action= True
    #while (not com.in_action):
    #    print(com.in_action)
    #    com.Readmsgs()
    for i in range(steps_forward):
        move(com,wheelspeeds(30,90,0))
        time.sleep(config.wait_time)
    while True:


        CenterOn('ball',com,pipeline,img_handler,config)

        GoTowards('ball',com,pipeline,img_handler,config,until=0.4,vel=15)

        Aling_Basket_Ball(com,pipeline,img_handler,config)

        GoTowards('ball',com,pipeline,img_handler,config,until=0.36,vel=5)
        print(Thrower_Strength)
        for i in range(5):
            move(com,wheelspeeds(15,90,0))
            thrower(com,Thrower_Strength)
            time.sleep(config.wait_time)
        move(com,stop())
        thrower(com,145)
    #Launch the ball
    #time.sleep(10)
    #print("Launch the ball")
    #move(com,left(config.cent_vel))
    #thrower(com,170)
    #time.sleep(10)


    pipeline.stop()
    com.close()

main()


