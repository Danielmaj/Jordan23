import serial
from mainboard import ComportMainboard
from time import sleep
from Motor import *

global com

def CreateConnection():
    com = ComportMainboard()
    com.open()
    return com

def move_forward(com):
    print('===========move forward')
    move(com,wheelspeeds(30,90,0))
    com.Readmsgs(verbos=True)

def stop_inplace(com):
    print('===========stopforward')
    move(com,wheelspeeds(0,90,0))
    com.Readmsgs(verbos=True)

def main():
    Myfield='A'
    My_ID = 'A'
    in_action=False
    try:
        com =CreateConnection()
        while True:
            sleep(0.02)
            if in_action:
                move_forward(com)
            else:
                stop_inplace(com)
            command = com.Readmsgs()
            print(command)
            if command is None:
                print('non object')
                continue
            command = command.strip()
            if command.startswith('<ref:a'):
                command = command.replace('-','')
                command=command[6:-1]
                Field_ID= command[0]
                Robot_ID = command[1]
                actual_command = command[2:]
                if (Field_ID == Myfield and (Robot_ID == My_ID or Robot_ID=='X')):
                    print('F:{},R:{},comd:{}'.format(Field_ID,Robot_ID,actual_command))
                    if actual_command == 'START':
                        in_action=True
                        print('let start now')
                    elif actual_command=='STOP':
                        in_action=False
                        print('lets stop now')
                    elif actual_command=='PING':
                        com.write('rf:aX{}ACK-----'.format(My_ID))
                        print('lets stop now')
    finally:
        com.close()
main()
