import pyrealsense2 as rs
import numpy as np
import cv2
import sys
sys.path.append('../')
from Image_Processing.Image_Handler import Image_Handler
from Hardware.mainboard import *
from Hardware.Motor import *
from time import sleep
#Connection to main board
com = ComportMainboard()
com.open()
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
tune_vel_big = 10
tune_vel_small = 2
rotate_vel = 30

def center_on_ball(coordinates):
    print(coordinates)
    x,y = coordinates
    pause = False

    if abs(x-320)>80:
        vel = tune_vel_big
    else:
        vel = tune_vel_small
    if x > 340:
       move(com,right(vel))
    elif x < 300:
       move(com,left(vel))
    else:
       print('we arrived =-==------------=========')
       move(com,stop())
       pause = True
    return pause   #sleep(0.01)


def rotate_to_ball():
    # Start streaming
    pipeline.start(config)
    img_handler = Image_Handler()
    rotate=0
    try:
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue
            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())

            coordinates = img_handler.LocateBallCenter(color_image)

            if coordinates is None:
               print('rotating',rotate)
               rotate+=1
               if rotate==20:
                   move(com,left(rotate_vel))
                   rotate=0
            else:
               rotate=0
               pause = center_on_ball(coordinates)
               if pause:
                  break
            sleep(0.01)

    finally:

        print('Finish centering on ball')
        pipeline.stop()
        com.close()
rotate_to_ball()
