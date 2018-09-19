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

def move_constant(vel):
    while true
        move(vel)
        time.sleep(0.08)


def Centerball():
    ''' Rotate until you find the green ball around center camera'''

    com = CreateConnection()
    com.launch_motor(100)

    pool = Pool(processes=2)
    see_ball = pool.map_async(LocateGreenBall)
    velrot = test_all_wheels(20)
    rotate = pool.map_async(move_constant,velrot)

    # Stop
    see_ball.wait()
    pool.close()
    pool.join()
    move(stop())

def GoToballStraight():
    '''Robot drives straight to the ball and does not rotate '''
    Centerball()

    #pool = Pool(processes=2)
    #see_ball = pool.map_async(LocateGreenBall)
    #vel = forward(30)
    #rotate = pool.map_async(move_constant,velrot)

    # Stop
    #see_ball.wait()
    #pool.close()
    #pool.join()
    #move(stop())
    #com.close()



def GotoBallAngle():
    '''Robot drives at an angle to the ball and does not rotate '''
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
