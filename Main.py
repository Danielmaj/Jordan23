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

def Test_motors(com):
    thrower(com,1500)
    move(com,stop())
    for i in range(3):
       move(com,left(10))
       sleep(1)
    move(com,stop())

def main():
    com =CreateConnection()
    Test_motors(com)
    com.close()
main()
