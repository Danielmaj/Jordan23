import serial
from mainboard import ComportMainboard
from time import sleep
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
    vel = [0,0,-power,+power]
    return vel
def stop():

    vel = [0,0,0,0]
    return vel

def rotate():

    vel = [30,30,30,30]
    return vel

def start():

    com = ComportMainboard()
    com.open()
    com.launch_motor(100)
    return com

def move(com,vel):

    com.write("sd:{}:{}:{}:{}".format(vel[0],vel[3],vel[2],vel[3]))

def main():

    com = start()
    for i in range(3):
       move(com,forward(30))
       #move(com,backward(30))
       sleep(1)
    com.close()

main()
