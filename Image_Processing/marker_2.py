import pyrealsense2 as rs
import numpy as np
import cv2
import cv2.aruco as aruco
#Connection to main board
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
vel = 5
# Start streaming
pipeline.start(config)
try:
    # print detector parameters
    print("detector params:")
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

finally:
    # Stop streaming
    print('Finish')
    pipeline.stop()
