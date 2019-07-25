import serial #module for serial port communication
import signal
import sys
import tty
import termios
import os
from picamera import PiCamera, Color
from time import sleep
from datetime import datetime, timedelta

def emergency(signal, frame):
    print('Something went wrong!')
    sys.exit(0)


def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)


demoCamera = PiCamera()
demoCamera.resolution=(500,480)
demoCamera.start_preview()

ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
i=0
try:
    while True:
        key=readkey()
        user = key + '\n'
        ser.write(user.encode('utf-8'))
        response = ser.readline()
        print(response.decode('utf-8'))
        if key=='t':
            i=i+1
            demoCamera.capture('/home/pi/Desktop/img/snapshot%03d.jpg' % i)            
except KeyboardInterrupt:
    ser.close()
    demoCamera.stop_preview()
        



'''
try:
    while 1:
        user = input() + '\n';
        ser.write(user.encode('utf-8'));
        response = ser.readline()
        print(response.decode('utf-8'))

except KeyboardInterrupt:
    ser.close()
'''