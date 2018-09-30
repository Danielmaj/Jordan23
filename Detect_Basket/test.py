import pyrealsense2 as rs
from collections import deque
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

# Start streaming
pipeline.start(config)
img_handler = Image_Handler()
def LocateBallCenter(frame):
	# define the lower and upper boundaries of the "green"
	# ball in the HSV color space, then initialize the
	# list of tracked points
	#greenLower = (29, 86, 6)
	#greenUpper = (64, 255, 255)
	greenLower = (60,100,40)
	greenUpper = (90, 255, 255)

	# resize the frame, blur it, and convert it to the HSV
	# color space
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, greenLower, greenUpper)
        #mask = cv2.inRange(hsv, (36, 0, 0), (70, 255,255))

	## slice the green
	imask = mask>0
	green = np.zeros_like(frame, np.uint8)
	green[imask] = frame[imask]

	## save 
	#cv2.imwrite("green.png", green)
        return green
	mask = cv2.erode(mask, None, iterations=1)
	mask = cv2.dilate(mask, None, iterations=1)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
	lenq = 10 # Maximum number of center points stored in memory

	pts = deque(maxlen=lenq)

	#only proceed if at least one contour was found
	if len(cnts) > 0:

	    #print(len(cnts))
	    # find the largest contour in the mask, then use
	    # it to compute the minimum enclosing circle and
	    # centroid
	    c = max(cnts, key=cv2.contourArea)
	    ((x, y), radius) = cv2.minEnclosingCircle(c)
	    M = cv2.moments(c)
	    # only proceed if the radius meets a minimum size
	    if radius > 7:
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
	return center
try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = LocateBallCenter(color_image)
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)

        # Stack both images horizontally
        images = np.hstack((color_image, depth_image))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        cv2.waitKey(1)

finally:
    # Stop streaming
    print('am done with you')
    pipeline.stop()
    com.close()
