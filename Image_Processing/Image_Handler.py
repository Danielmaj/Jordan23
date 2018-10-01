import numpy as np
import cv2
from collections import deque
import pyrealsense2 as rs

class Image_Handler():

    def LocateBallCenter(self,frame):
        # define the lower and upper boundaries of the "green"
        # ball in the HSV color space, then initialize the
        # list of tracked points
        #greenLower = (29, 86, 6)
        #greenUpper = (64, 255, 255)
        #greenLower = (40,40,40)
        #greenUpper = (70, 255, 255)
        #Last Best
    	#greenLower = (60,100,100)
   	#greenUpper = (90,200,160)
        #New Best
        #greenLower = (15,27,56)
        #greenUpper = (90,255,146)
        #New Best
        greenLower = (25,110,56)
        greenUpper = (90,255,146)
        

        # resize the frame, blur it, and convert it to the HSV
        # color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        #mask = cv2.erode(mask, None, iterations=1)
        #mask = cv2.dilate(mask, None, iterations=1)

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
            if radius > 5:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        return center#,radius

    def howfar(self,depth_frame,coordinates):
        '''Returns the distance  in mm around a center point a square of size s'''
        '''The camera is inclined so this brings some problems '''

        size = 5
        cam_angle = 5
        cam_height = 200

        # Distance from the camera plane(not camera center) to the object in mm
        xc,yc = coordinates

        xmin = max(xc-size,0)
        xmax = min(xc+size,640)
        ymin = max(yc-size,0)
        ymax = min(yc+size,480)

        avg_dist = 0
        for x in range(xmin, xmax):
            for y in range(ymin, ymax):
                depth = depth_frame.get_distance(x,y)
                avg_dist +=  depth_frame.get_distance(x,y)
        avg_dist /= (xmax - xmin + ymax - ymin)
        # Distance respect to the camera
        return avg_dist
