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

def move(com,vel):
    com.write("sd:{}:{}:{}:{}".format(vel[0],vel[3],vel[2],vel[3]))
    #print(com.connection.readline())
    #com.connection.flush()

def move2(vel):
    com.write("sd:{}:{}:{}:{}".format(vel[0],vel[3],vel[2],vel[3]))
    #print(com.connection.readline())
    #com.connection.flush()


def Centerball():

    com = CreateConnection()
    com.launch_motor(100)

    # Rotate until you find the green ball
    pool = Pool(processes=2)
    see_ball = pool.map_async(LocateGreenBall)
    velrot = test_all_wheels(20)
    rotate = pool.map_async(move2(velrot))

    see_ball.wait()
    pool.close()
    pool.join()
    move2(stop())
    center

    # Adjust the position to the center



def main():
    com =CreateConnection()
    com.launch_motor(100)
    for i in range(3):
       move(com,forward(30))
       sleep(1)
    move(com,stop())

    for i in range(3):
       move(com,backward(30))
       sleep(1)
    com.close()
main()
