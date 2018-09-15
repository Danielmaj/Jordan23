import serial
import import sys
sys.path.append('../')
from comunication/mainboard.py import ComportMainboard


def forward(com):

    vel = [0,30,30,0]
    return vel


def stop():

    vel = [0,0,0,0]
    return vel

def rotate():

    vel = [30,30,30,0]
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
    move(com,forward())

main()
