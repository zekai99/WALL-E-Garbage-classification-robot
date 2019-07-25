from __future__ import print_function
import paho.mqtt.client as mqtt
import time
import base64

USERID =  "sws009"
PASSWORD = "shorthaircat"
resp_callback = None

def on_connect(client, userdata, flags, rc):
    print("Connected. Result code is %d."%(rc))
    client.subscribe(USERID+"/IMAGE/predict")

def on_message(client, userdata, msg):
    # print("Received message from server.", msg.payload)
    print("Received message from server.")
    tmp = msg.payload.decode("utf-8")
    ss = tmp.split(":")
    img = bytes(ss[int(ss[0])+1], encoding = "utf8")
    print("Saving picture...")
    #with open("%03d.jpg"%p_name, "wb") as f:
    # 这里不能用全局变量重命名。。很奇怪
    with open("tmp.jpg", "wb") as f:
        f.write(base64.b64decode(img))
    
    if resp_callback is not None:
        #resp_callback(str[0], float(str[1]), int(str[2]))
        resp_callback(ss)

def setup():
    global client

    client = mqtt.Client()
    # client.username_pw_set(USERID, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("192.168.43.94", 1883, 30)
    client.loop_start()

def load_image(filename):
    with open(filename, "rb") as f:
        data=f.read()
    return data

def send_image(filename):
    img = load_image(filename)
    client.publish(USERID+"/IMAGE/classify", img)

def resp_handler(ss):
    print("\n -- Response -- ")
    #str = tmp.split(":")
    n = int(ss[0])
    for i in range(n):
        t = i + 1
        # 小于0：往左偏离中心像素  大于0：往右
        print("Object %d has a pixel value of %d from the center."%(t, int(ss[t])))
    print("\n\n")
    #print("Label: %s"%(label))
    #print("Probability: %3.4f"%(prob))
    #print("Index: %d"%(index))

def main():
    global resp_callback

    setup()
    resp_callback = resp_handler
    print("Waiting 2 seconds before sending.")
    time.sleep(2)
    print("Sending tulip.jpg")
    send_image("tulip.jpg")
    print("Done. Waiting 5 seconds before sending.")
    time.sleep(5)
    print("Sending tulip2.jpg")
    send_image("tulip2.jpg")
    print("Done")
    while True:
        pass

if __name__ == '__main__':
    main()