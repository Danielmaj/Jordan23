import serial
from Hardware.mainboard import ComportMainboard
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
