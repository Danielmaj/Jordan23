import numpy as np
import sys
sys.path.append('../')
from Hardware.mainboard import *
from Hardware.Motor import *
from time import sleep
#Connection to main board
com = ComportMainboard()
com.open()
com.launch_motor(10)
img_handler = Image_Handler()
def Get_frame():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    # Start streaming
    pipeline.start(config)
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    if not depth_frame or not color_frame:
       continue
    color_image = np.asanyarray(color_frame.get_data())

def Go_Some_Where(coordinates):
    print(coordinates)
    com.launch_motor(100)
    if coordinates[0]>340:

       move(com,right(10))
       sleep(0.01)
    elif coordinates[0]<300:
       move(com,left(10))
       sleep(0.01)
    else:
       move(com,stop())
       sleep(0.01)

try:
    while True:

        # Wait for a coherent pair of frames: depth and color

        # Convert images to numpy arrays
        #depth_image = np.asanyarray(depth_frame.get_data())
        color_image = Get_frame()
        coordinates = img_handler.LocateBallCenter(color_image)
        if coordinates is None:
           print('rotating')
           move(com,right(10))
           sleep(0.01)
        else:
           Go_Some_Where(coordinates)
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
