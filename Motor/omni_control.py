import numpy as np

#Given a direction, angle and angular velocity returns speed of the wheels
#wheelLinearVelocity = robotSpeed * cos(robotDirectionAngle - wheelAngle) + wheelDistanceFromCenter * robotAngularVelocity
def wheelspeeds(rspeed,rangle,rangular):

    wheels_dist = np.array([0.115, 0.115,0.115]) #Not sure of the exact distance
    wheels_angle = np.radians(np.array([0, 120, 240]))
    rangle = np.radians(np.array([rangle, rangle, rangle]))
    rspeed = np.array([rspeed, rspeed, rspeed])
    rangular = np.array([rangular, rangular, rangular])

    vel = rspeed*np.cos(rangle - wheels_angle) + wheels_dist*rangular

return vel
