import serial
import threading
import time
import subprocess
import rospy

# Martin Appo implementation of comunication with mainboard. File from
#https://bitbucket.org/MartinAppo/diploaf-2017/src/master/hardware_module/src/hardware_module/comport_mainboard.py

class ComportMainboard(threading.Thread):
    connection = None
    connection_opened = False
    Myfield ='A'
    My_ID = 'A'
    in_action = False
    def __init__(self):
        threading.Thread.__init__(self)

    def open(self):
        try:
            ports = subprocess.check_output('ls /dev/ttyACM0', shell=True).split('\n')[:-1]
        except:
            print('mainboard: /dev/ttyACM empty')
            return False
        self.connection_opened = False
        for port in ports:  # analyze serial ports
            try:
                while not self.connection_opened and not rospy.is_shutdown():
                    self.connection = serial.Serial(port, baudrate=115200, timeout=0.8, dsrdtr=True)
                    self.connection_opened = self.connection.isOpen()
                    time.sleep(0.5)
                self.connection.flush()
                print "mainboard: Port opened successfully"
            except Exception as e:
                print(e)
                continue

        return self.connection_opened

    def write(self, comm):
        if ((self.connection is not None) and self.in_action):
            try:
                self.connection.write(comm + '\n')
            except:
                print('mainboard: err write ' + comm)

    def write_ref(self, comm):
        if self.connection is not None:
            try:
                self.connection.write(comm + '\n')
            except:
                print('mainboard: err write ' + comm)

    def servo(self, value):
        msg = "v{}".format(value)
        if self.connection_opened and self.in_action:
            self.write(msg)

    def launch_motor(self, value):
        if self.connection_opened and self.in_action:
            self.write("d{}".format(value))

    def close(self):
        if self.connection is not None and self.connection.isOpen():  # close coil
            try:
                self.connection.close()
                print('mainboard: connection closed')
            except:
                print('mainboard: err connection close')
            self.connection = None

    def Readmsgs(self,verbos=False):
	try:
            self.connection.flush()
            txt = self.connection.readline()

            #Handling the message if its from referee
            if txt is not None:
                command = txt.strip()
                if command.startswith('<ref:a'):
                    command = command.replace('-','')
                    command=command[6:-1]
                    Field_ID= command[0]
                    Robot_ID = command[1]
                    actual_command = command[2:]
                    if (Field_ID == self.Myfield and (Robot_ID == self.My_ID or Robot_ID=='X')):
                        print('F:{},R:{},comd:{}'.format(Field_ID,Robot_ID,actual_command))
                        if actual_command == 'START':
                            self.in_action=True
                        elif actual_command=='STOP':
                            self.in_action=False
                        elif actual_command=='PING':
                            self.write_ref('rf:aX{}ACK-----'.format(My_ID))
            if verbos:
                print(txt)
            return txt
	except Exception as ex:
	    print(ex)

    def run(self):
        if self.open():  # open serial connections
            print('mainboard: opened')
        else:
            print('mainboard: opening failed')
            self.close()
            return
