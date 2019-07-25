from __future__ import print_function
import paho.mqtt.client as mqtt
import numpy as np
from PIL import Image
from io import BytesIO
import predict_mqtt
import os
import base64

USERID =  "sws009"
PASSWORD = "shorthaircat"

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(ROOT_DIR, "tmp")
TMP_FILE = os.path.join(TMP_DIR, "tmp.jpg")
TMP_FILE_RCNN = os.path.join(TMP_DIR, "tmp_rcnn.jpg")
# TMP_FILE = "/tmp/"+USERID+".jpg"
# dict={0:'daisy',1:'dandelion',2:'roses',3:'sunflowers',4:'tulips'}

def load_image(filename):
    with open(filename, "rb") as f:
        data=f.read()
    return data

def on_connect(client, userdata, flags, rc):
    print("Connected with result code %d."%(rc))

    client.subscribe(USERID+"/IMAGE/classify")

def on_message(client, userdata, msg):
    print("Received message. Writing to %s."%(TMP_FILE))
    img = msg.payload
    with open(TMP_FILE, "wb") as f:
        f.write(img)

    s = predict_mqtt.classify_mqtt(TMP_FILE, TMP_FILE_RCNN)
    # print("Classified as %s with certainty %3.4f."%(label, prob))
    data = load_image(TMP_FILE_RCNN)
    print("Sending...")
    client.publish(USERID+"/IMAGE/predict", s+":"+str(base64.b64encode(data), 'utf-8'))
    # client.publish(USERID+"/IMAGE/predict", str(base64.b64encode(data), 'utf-8'))
    # client.publish(USERID+"/IMAGE/predict", s)

def setup():
    global dict
    global client

    client = mqtt.Client(transport="websockets")

    client.username_pw_set(USERID, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting")
    x = client.connect("pi.smbox.co", 80, 30)
    client.loop_start()

def main():
    setup()
    while True:
        pass

if __name__ == '__main__':
    main()

