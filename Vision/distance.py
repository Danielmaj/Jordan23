import pyrealsense2 as rs
import numpy as np
import cv2


def howfar(depth_frame,coordinate,size):
    '''Returns the distance  in mm around a center point a square of size s'''
    '''The camera is inclined so this brings some problems '''

    # Distance from the camera plane(not camera center) to the object in mm
    xc,yc = coordinate
    avg_dist = 0

    xmin = max(xc-size,0)
    xmax = min(xc+size,640)
    ymin = max(yc-size,0)
    ymax = min(yc+size,480)

    depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics

    for x in range(xmin, xmax)
        for y in range(ymin, ymax)
            depth = depth_frame.get_distance(x,y)
            avg_dist = + depth
            #depth_point = rs.rs2_deproject_pixel_to_point(depth_intrin, [y, x], depth)
            # depth_point x y z
    avg_dist /= (xmax - xmin + ymax - ymin)
    # Distance respect to the camera

    cam_angle = 45
    cam_height = 200


    return dist
