from __future__ import print_function
import paho.mqtt.client as mqtt
import numpy as np
from PIL import Image
from io import BytesIO
import predict_mqtt
import os
import base64
import time
import shutil 
import threading

USERID =  "sws009"
PASSWORD = "shorthaircat"
lock = threading.Lock()

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(ROOT_DIR, "tmp")
TMP_FILE = os.path.join(TMP_DIR, "tmp.jpg")
#TMP_COPY = os.path.join(TMP_DIR, "copy.jpg")
TMP_FILE_RCNN = os.path.join(TMP_DIR, "tmp_rcnn.jpg")

# TMP_FILE = "/tmp/"+USERID+".jpg"
# dict={0:'daisy',1:'dandelion',2:'roses',3:'sunflowers',4:'tulips'}

def load_image(filename):
    with open(filename, "rb") as f:
        data=f.read()
    return data

img = load_image(TMP_FILE)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code %d."%(rc))

    client.subscribe(USERID+"/IMAGE/classify")

def on_message(client, userdata, msg):
    global img
    print("Received message. Writing to %s."%(TMP_FILE))
    lock.acquire()
    img = msg.payload
    lock.release()

def setup():
    global dict
    global client

    client = mqtt.Client()

    # client.username_pw_set(USERID, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting")
    x = client.connect("192.168.43.94", 1883, 30)
    client.loop_start()

def doing():
    global img
    while True:
        lock.acquire()
        with open(TMP_FILE, "wb") as f:
            f.write(img)
        lock.release()
        s = predict_mqtt.classify_mqtt(TMP_FILE, TMP_FILE_RCNN)
        data = load_image(TMP_FILE_RCNN)
        print("Sending...")
        client.publish(USERID+"/IMAGE/predict", s+":"+str(base64.b64encode(data), 'utf-8'))

def main():
    t1 = threading.Thread(target=setup)
    setup()
    t2 = threading.Thread(target=doing)
    doing()

if __name__ == '__main__':
    main()

