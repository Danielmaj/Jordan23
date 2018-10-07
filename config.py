"""
Jordan 23
Base Configurations class.
"""
import math
import numpy as np

# Base Configuration Class
# Don't use this class directly to try things. Instead, sub-class it and override
# the configurations you need to change.

class Config(object):
    """Base configuration class. To try configurations, create a
    sub-class that inherits from this one and override properties
    that need to be changed.
    """
    # Name the configurations. For example "Week 4 Task "
    # Useful if your code needs to do things differently depending on which
    # experiment is running.
    NAME = 'basic'  # Override in sub-classes

    # Image form camera width and height
    frame_width = 640
    frame_heigth = 480

    # Center of ball in the frame
    robot_center_x = 340

    # Center Basket in the frame
    bask_center_x = 320


    # How many frames to wait before starting to rotate again to locate some object
    rot_wait =  10

    # velocity of Rotation to locate object
    rot_vel =  12

    # Precision of rotation centering on object. Error allowed in pixels when rotating centering on an object
    cent_precision = 15

    # Velocity of centering on an object
    cent_vel = 5

    # Time to sleep between motor comands to avoid too many comands
    wait_time = 0.1

    # Moving forward starting from the corner in omniwheel coordinates (velocity,angle,angular velocity)
    corner_omni_vel = np.array([15, 90, 0])

    # Parameters to rotate around the Ball
    around_ang_vel = 30

    #Parameters to locate the Basket
    # basket blue
    lower_blue = np.array([95, 160, 100])
    upper_blue = np.array([105, 255, 130])

    # basket magenta
    lower_magenta = np.array([169, 130, 105])
    upper_magenta = np.array([180, 255, 255])


    def __init__(self):
        """Set values of computed attributes."""
        # Maximum x to consider the robot centred respect to an object
        self.max_cent_x = self.robot_center_x + self.cent_precision
        self.min_cent_x = self.robot_center_x - self.cent_precision
        self.max_bask_x = self.bask_center_x + 10
        self.min_bask_x = self.bask_center_x - 10

    def display(self):
        """Display Configuration values."""
        print("\nConfigurations:")
        for a in dir(self):
            if not a.startswith("__") and not callable(getattr(self, a)):
                print("{:30} {}".format(a, getattr(self, a)))
        print("\n")
