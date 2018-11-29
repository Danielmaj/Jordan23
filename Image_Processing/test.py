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
DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07"]

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
# Configure depth and color streams
pipeline = rs.pipeline(rs.context())
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
# Start streaming
pipeline.start(config)
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
    #as_json_object['controls-color-white-balance-auto'] = 'False'
    as_json_object['controls-color-autoexposure-auto']='True'
    as_json_object['controls-autoexposure-auto']= 'True'
    #as_json_object['controls-color-gain']=32
    print('I am hero')
    
    # The C++ JSON parser requires double-quotes for the json object so we need
    # to replace the single quote of the pythonic json to double-quotes
    json_string = str(as_json_object).replace("'", '\"')
    advnc_mode.load_json(json_string)
    time.sleep(2)

except Exception as e:
    print(e)

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
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        coordinates = img_handler.LocateBallCenter(color_image,greenLower ,greenUpper)
        print(coordinates)
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
