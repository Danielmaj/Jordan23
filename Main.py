import serial
from Comunication.mainboard import ComportMainboard
from time import sleep
from Motor.direction import * 
def CreateConnection():
    com = ComportMainboard()
    com.open()
    return com
def move(com,vel):
    com.write("sd:{}:{}:{}:{}".format(vel[0],vel[3],vel[2],vel[3]))
    #print(com.connection.readline())
    #com.connection.flush()

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
