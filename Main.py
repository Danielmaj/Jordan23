import serial
from Hardware.mainboard import ComportMainboard
from time import sleep
from Hardware.Motor import *
from Image_Processing.locateBall import *

from multiprocessing import Pool
global com

def CreateConnection():
    com = ComportMainboard()
    com.open()
    return com

def Readmsgs(com):
    try:
       com.connection.flush()
       print(com.connection.readline())
    except Exception as ex:
       print(ex)

def move(com,vel):
    com.write("sd:{}:{}:{}".format(vel[0],vel[1],vel[2]))
    Readmsgs(com)

def thrower(com,value):
    com.write("d:{}".format(value))
    Readmsgs(com)
def Test_motors(com):
    #thrower(com,1500)
    move(com,stop())
    for i in range(3):
       move(com,right(30))
       sleep(1)
    move(com,stop())

    for i in range(3):
       move(com,left(30))
       sleep(1)
def main():
    com =CreateConnection()
    com.launch_motor(100)
    Test_motors(com)
    com.close()
main()
