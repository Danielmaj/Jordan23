import pyrealsense2 as rs
import numpy as np
import cv2
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
vel = 5
def Go_Some_Where(coordinates):
    print(coordinates)
    x,y = coordinates
    pause = False
    #com.launch_motor(100)
    if x > 330:
       move(com,right(vel))
    elif x < 310:
       move(com,left(vel))
    else:
       print('we arrived =-==------------=========')
       move(com,stop())
       pause = True
    return pause   #sleep(0.01)

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
        #depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        coordinates = img_handler.LocateBallCenter(color_image)
        if coordinates is None:
           print('rotating',rotate)
           rotate+=1
           if rotate==10:
               move(com,left(20))
               rotate=0
        else:
           rotate=0
           pause = Go_Some_Where(coordinates)
           if pause:
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
    print('am done with you')
    pipeline.stop()
    com.close()
