import pyrealsense2 as rs
import numpy as np
import cv2
import math
from Image_Handler import Image_Handler
import sys
sys.path.append('../')
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
vel = 10
def Rotate_towards_ball(coordinates):
    print(coordinates)
    x,y = coordinates
    centred = False
    #com.launch_motor(100)
    if x > 540:
       move(com,right(vel))
    elif x < 120:
       move(com,left(vel))
    else:
       print('we arrived =-==------------=========')
       move(com,stop())
       centred = True
    return centred   #sleep(0.01)

# Start streaming
pipeline.start(config)
img_handler = Image_Handler()
rotate=0
centred = False
try:
    for i in range(80):
        move(com,wheelspeeds(15,90,0)) #Forward
        sleep(0.1)
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

        if not centred:
            if coordinates is None:
               print('rotating',rotate)
               rotate+=1
               if rotate==10:
                   move(com,left(20))
                   rotate=0
            else:
		rotate = 0
		centred = Rotate_towards_ball(coordinates)
	    sleep(0.01)
        else: # Go towards the ball
            if coordinates is None: #If you lose sight of the ball rotate again
                centred = False
            else:
                #dist = img_handler.howfar(depth_frame,coordinates)
                x,y = coordinates
		dist = depth_frame.get_distance(int(x),int(y))
                print("distance",dist)
		if dist > 0.3:
                    print("moving towards the ball")
		    dx = (x -320)/320
                    angle_to_ball = 90 + 20*dx
		    move(com,wheelspeeds(5,angle_to_ball,0)) #Forward
                    #move(com,forward(-10))
		else:
                    if dist > 0.01:
		        move(com,stop())
                   	break
                sleep(0.01)

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
        #images = np.hstack((color_image, depth_colormap))

        # Show images
        #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        #cv2.imshow('RealSense', images)
        #cv2.waitKey(1)

finally:
    # Stop streaming
    print('Finish')
    pipeline.stop()
    com.close()
