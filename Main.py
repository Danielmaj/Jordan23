import serial
from Hardware.mainboard import ComportMainboard
from time import sleep
from Hardware.Motor import *
from Image_Processing.Image_Handler import *

from multiprocessing import Pool
global com

def CreateConnection():
    com = ComportMainboard()
    com.open()
    com.launch_motor(100)
    return com

def Test_motors(com):
    move(com,wheelspeeds(10,90,0))

    #thrower(com,1500)
    #com.write("d:{}".format(2000))
    
    #thrower(com,2000)
    com.Readmsgs(verbos=True)
    #thrower(com,1500)
    #sleep(1)
    #thrower(com,2000)
    #move(com,stop())
    #for i in range(3):
    #   move(com,left(30))
    #   sleep(1)
    #move(com,stop())

def main():
    com =CreateConnection()
    Test_motors(com)
    com.close()
main()
