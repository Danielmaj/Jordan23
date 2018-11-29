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
from Image_Processing.Image_Handler import Image_Handler
import numpy as np
import json

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


positions=None
def click(event, x, y, flags, param):
        global positions
	if event == cv2.EVENT_LBUTTONDOWN:
		positions = (x, y)
def PrepareCamera():
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)

        pipeline.start(config)
        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        align_to = rs.stream.color
        align = rs.align(align_to)

        ctx = rs.context()
        devices = ctx.query_devices()
        for dev in devices:
            if dev.supports(rs.camera_info.product_id) and dev.supports(rs.camera_info.name):
                print("Found camera device: {}".format(dev.get_info(rs.camera_info.name)))
                sensors = dev.query_sensors()
                for sensor in sensors:
                    if sensor.get_info(rs.camera_info.name) == "RGB Camera" and sensor.supports(
                            rs.option.exposure) and sensor.supports(rs.option.gain):
                        print("Setting RGB camera sensor settings")
                        sensor.set_option(rs.option.enable_auto_exposure, 1)
                        sensor.set_option(rs.option.white_balance, 3000)
                        sensor.set_option(rs.option.enable_auto_white_balance, 0)
                        sensor.set_option(rs.option.gain, 0)
                        print("exposure: {}".format(sensor.get_option(rs.option.exposure)))
                        print("white balance: {}".format(sensor.get_option(rs.option.white_balance)))
                        print("gain: {}".format(sensor.get_option(rs.option.gain)))
                        print(
                            "auto exposure enabled: {}".format(sensor.get_option(rs.option.enable_auto_exposure)))
                        time.sleep(2)
                        sensor.set_option(rs.option.enable_auto_exposure, 0)
                        print(
                            "auto exposure enabled: {}".format(sensor.get_option(rs.option.enable_auto_exposure)))
                        print("exposure: {}".format(sensor.get_option(rs.option.exposure)))  # 166
                        print("white balance: {}".format(sensor.get_option(rs.option.white_balance)))
                        print("gain: {}".format(sensor.get_option(rs.option.gain)))  # 64
                        break
		break
	return pipeline
pipeline = PrepareCamera()
#config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
#config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)




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

def LocateBallCenter(frame,greenLower=None,greenUpper=None):
    # define the lower and upper boundaries of the "green"
    # ball in the HSV color space, then initialize the
    #new ones generated 26 November
    if greenLower is None:
        greenLower = (9, 115,  26)
    if greenUpper is None:
        greenUpper = (82, 255,  68)
    # resize the frame, blur it, and convert it to the HSV
    # color space
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    erode_kernel = np.ones((4, 4), np.uint8)
    mask = cv2.erode(mask, erode_kernel, iterations=1)
    dilate_kernel = np.ones((10, 10), np.uint8)
    mask = cv2.dilate(mask, dilate_kernel, iterations=1)
    imask = mask>0
    green = np.zeros_like(frame, np.uint8)
    green[imask] = frame[imask]
    return green,hsv,imask


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

def Smart_ball_detector(regular_image):
    self.balls_mask = np.zeros((conf.HEIGHT, conf.WIDTH, 1), dtype=np.uint8)

try:
    update = threading.Thread(target=UpdateLower_Upper)
    update.start()
    h = []
    s = []
    v = []
    img_handler = Image_Handler()
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_numpy = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        coordinates = img_handler.LocateBallCenter(color_image,greenLower ,greenUpper)
        if coordinates:
            print('coords:{},depth:{}'.format(coordinates,np.median(depth_numpy[imask])))
        #depth_image,hsv = LocateBallCenter_old(color_image)
        depth_image,hsv,imask= LocateBallCenter(color_image,greenLower ,greenUpper)
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
            h.append(hsv[y,x][0])
            s.append(hsv[y,x][1])
            v.append(hsv[y,x][2])
            greenLower =np.array([min(h),min(s),min(v)])
            greenUpper = np.array([max(h),max(s),max(v)])
            print(h[-1],s[-1],v[-1])
            print(greenLower,greenUpper)
            positions=None
        cv2.waitKey(1)
finally:
    # Stop streaming
    print('am done with you')
    terminate_thread(update)
    pipeline.stop()
