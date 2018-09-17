import numpy as np
import cv2
from collections import deque

def LocateBallCenter(frame):
    # define the lower and upper boundaries of the "green"
    # ball in the HSV color space, then initialize the
    # list of tracked points
    greenLower = (29, 86, 6)
    greenUpper = (64, 255, 255)

    # resize the frame, blur it, and convert it to the HSV
    # color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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

        print(len(cnts))
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

def LocateGreenBall():

    lenq = 10 # Maximum number of center points stored in memory
    pts = deque(maxlen=lenq)

    #grab the reference to the webcam
    camera = cv2.VideoCapture(1)

    while len(pts) < lenq:
        # grab the current frame
        (grabbed, frame) = camera.read()
        center  =  LocateBallCenter(frame)

        if center is not None:
            # update the points queue
            pts.appendleft(center)
        #time.sleep(0.01)

    # We average the location to avoid outliers
    ball = center = (int(0), int(0))
    for c in pts:
        ball = ball + c
    ball /= lenq

    return ball


def CenterOnGreenBall():

    #grab the reference to the webcam
    camera = cv2.VideoCapture(1)
    precision = 20 # How far from the center we give as good

    while True:
        # grab the current frame
        (grabbed, frame) = camera.read()
        xc = frame.size[0]/2 # Horizontal center of the image
        center  =  LocateBallCenter(frame)

        if center is not None:
            x,y = center
            if (x < xc + precision) and  (x > xc - precision)
                error = x - xc
                break

    #print('Distance from center:',error)
    return error
