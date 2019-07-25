from __future__ import print_function
from tensorflow.python.keras.models import load_model
import tensorflow as tf
import numpy as np
from PIL import Image
import serial #module for serial port communication
import signal
import sys
import tty
import termios
import os
from picamera import PiCamera, Color
from time import sleep
from datetime import datetime, timedelta
import io

#MODEL_NAME="flowers.hd5"
dict={0: "Maine_Coon", 1: "Ocelot", 2: "Singapura", 3: "Turkish_Van"}
graph=tf.get_default_graph()

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

def classify(model,image):
    global graph
    with graph.as_default():
        result=model.predict(image)
        themax=np.argmax(result)
    return(dict[themax],result[0][themax],themax)
def load_image(image_fname):
    img=Image.open(image_fname)
    img=img.resize((249,249))
    imgarray=np.array(img)/255.0
    final=np.expand_dims(imgarray,axis=0)
    return final


def main():
    #model=load_model(MODEL_NAME)
    model=load_model("cats.hd5")
    demoCamera = PiCamera()
    demoCamera.resolution=(500,480)
    demoCamera.start_preview()

    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    #i=0
    try:
        while True:
            key=readkey()
            user = key + '\n'
            ser.write(user.encode('utf-8'))
            response = ser.readline()
            print(response.decode('utf-8'))
            if key=='t':
                #i=i+1
                #demoCamera.capture('/home/pi/Desktop/img/snapshot%03d.jpg' % i)
                stream=io.BytesIO()
                demoCamera.capture(stream, format='jpeg') 
                img=load_image(stream)
                label,prob,_=classify(model,img)
                print("we think with certainty %3.2f that it is %s."%(prob,label))
    except KeyboardInterrupt:
        ser.close()
        demoCamera.stop_preview()

if __name__=="__main__":
    main()
    