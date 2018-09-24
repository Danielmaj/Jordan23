from std_msgs.msg import String
import sys
sys.path.append('../')
from Hardware.mainboard import *
from Hardware.Motor import *
from time import sleep
#Connection to main board
com = ComportMainboard()
com.open()
com.launch_motor(100)

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data.data)

def listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # name are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber('ball_coordinates', String, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    try:
        listener()
    finally:
        # Stop streaming
        print('am done with you')
        pipeline.stop()
        com.close()
    




# Configure depth and color streams
veloceity = 1
def Go_Some_Where(coordinates):
    print(coordinates)
    x,y = coordinates
    pause = False
    #com.launch_motor(100)
    if x > 340:
       move(com,right(veloceity))
    elif x < 300:
       move(com,left(veloceity))
    else:
       move(com,stop())
       pause = True
    return pause   #sleep(0.01)

# Start streaming
rotate=0
try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        #depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        coordinates = img_handler.LocateBallCenter(color_image)
        if coordinates is None:
           print('rotating',rotate)
           rotate+=1
           if rotate==10:
               move(com,right(10))
               rotate=0
        else:
           rotate=0
           pause = Go_Some_Where(coordinates)
           if pause:
              break
        sleep(0.2)

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
        #images = np.hstack((color_image, depth_colormap))

        # Show images
        #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        #cv2.imshow('RealSense', images)
        #cv2.waitKey(1)

