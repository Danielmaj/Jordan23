import serial
from Comunication.mainboard import ComportMainboard
from time import sleep
from Motor.direction import *
from Vision.locateball import *
from multiprocessing import Pool
global com

def CreateConnection():
    com = ComportMainboard()
    com.open()
    return com

def move(vel):
    com.write("sd:{}:{}:{}:{}".format(vel[0],vel[3],vel[2],vel[3]))
    #print(com.connection.readline())
    #com.connection.flush()

def move_eternally(vel):
    while true
        com.write("sd:{}:{}:{}:{}".format(vel[0],vel[3],vel[2],vel[3]))
        time.sleep(0.08)
    #print(com.connection.readline())
    #com.connection.flush()


def Centerball():

    com = CreateConnection()
    com.launch_motor(100)

    # Rotate until you find the green ball
    pool = Pool(processes=2)
    see_center_ball = pool.map_async(CenterOnGreenBall)
    velrot = test_all_wheels(15)
    rotate = pool.map_async(move_eternally(velrot))

    see_center_ball.wait(timeout=2) # Wait until you see the ball in the center or 2 seconds
    pool.close()
    pool.join()
    move(stop())


def main():
    com =CreateConnection()
    com.launch_motor(100)
    for i in range(3):
       move(forward(30))
       sleep(1)
    move(stop())

    for i in range(3):
       move(backward(30))
       sleep(1)
    com.close()
main()
