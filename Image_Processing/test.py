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
import threading
import ctypes

def terminate_thread(thread):
    """Terminates a python thread from another thread.

    :param thread: a threading.Thread instance
    """
    if not thread.isAlive():
        return

    exc = ctypes.py_object(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread.ident), exc)
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

positions=None
def click(event, x, y, flags, param):
        global positions
	if event == cv2.EVENT_LBUTTONDOWN:
		positions = (x, y)
 

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
#config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
#config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)


greenLower = (60,100,100)
greenUpper = (90, 200, 160)

greenLower = (25,110,56)
greenUpper = (90,255,146)
#greenLower = (40,100,40)
#greenUpper = (90,255,255)
def UpdateLower_Upper():
	global greenLower,greenUpper
        while True:
                print('Enter values to print')
		x = input()
                print(type(x),x)
                numbers = [int(j) for j in x]
                greenLower=np.array(numbers[0:3])
                greenUpper=np.array(numbers[3:6] )
		print(x)
def LocateBallCenter(frame):
        global greenLower,greenUpper
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
        return green,hsv
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
    update = threading.Thread(target=UpdateLower_Upper)
    update.start()
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
        depth_image,hsv = LocateBallCenter(color_image)
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)

        # Stack both images horizontally
        images = np.hstack((color_image, depth_image))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('RealSense',click)
        cv2.imshow('RealSense', images)
        if positions is not None:
            #print(positions[0],positions[1],depth_image.shape)
            x = positions[0]
            y = positions[1]
            print(hsv[y,x][0],hsv[y,x][1],hsv[y,x][2])
            print('y:{},x:{}'.format(y,x))
            positions=None
        cv2.waitKey(1)

finally:
    # Stop streaming
    print('am done with you')
    terminate_thread(update)
    pipeline.stop()
