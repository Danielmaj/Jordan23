import numpy as np
import cv2
from collections import deque
import pyrealsense2 as rs

class Image_Handler():

    def LocateBallCenter(self,frame):
        # define the lower and upper boundaries of the "green"
        # ball in the HSV color space, then initialize the
        # list of tracked points

    	greenLower = (35,208,90)
   	    greenUpper = (58,255,169)

        # resize the frame, blur it, and convert it to the HSV
        # color space
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, greenLower, greenUpper)
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
            # only proceed if the basket meets a minimum size
            if w*h > 20:
                center = (int(x), int(y))
        return center
