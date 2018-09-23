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

def forward(power):
    vel = [0,0,-power,power]
    return vel

def backward(power):
    vel = [0,0,power,-power]
    return vel

def right(power):
    vel = [0,0,power,power]
    return vel

def left(power):
    vel = [0,0,-power,-power]
    return vel

def stop():
    vel = [0,0,0,0]
    return vel

def test_all_wheels(power):
    vel = [0,power,power,power]
    return vel

def test_thrower():
    vel = [power,0,0,0]
    return vel