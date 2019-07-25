#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
from bottle import get,post,run,request,template,route,static_file
import time
import serial #module for serial port communication
import threading
import fcntl
import os


assets_path='./assets'
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
n_objects=0
param1=0
# 左转函数
def left():
    ser.write("a".encode('utf-8'))

# 右转
def right():
    ser.write("d".encode('utf-8'))
# 前进
def go():
    ser.write("w".encode('utf-8'))

# 后退
def back():
    ser.write("s".encode('utf-8'))

# 停止
def stop():
    ser.write("x".encode('utf-8'))

def file_read():
    try:
        f = open('data.txt', 'r')
        fcntl.flock(f, fcntl.LOCK_EX)
        tmp=f.read()
        fcntl.flock(f, fcntl.LOCK_UN)
    finally:
        if f:
            f.close()
    tmp=tmp.split(":")
    return tmp

def loop_read():
    print('thread %s is running...' % threading.current_thread().name)
    global ss
    global n_objects
    global param1
    while True:
        size = os.path.getsize('data.txt')
        if (size==0):
            continue
        ss=file_read()
        if (ss==[]):
            continue
        if (param1>int(ss[0])):
            continue
        time.sleep(2)
        n_objects = int(ss[0])
        print("obiect:%d"%param1)
        print(ss[param1])
        print(ss)
        if (param1!=0):
            if (int(ss[param1])>30):
                right()
            if (int(ss[param1])<-30):
                left()
            if (int(ss[param1])<30 and int(ss[param1])>-30):
                param1=0
                go()
                go()
                go()
                go()
                go()
                go()
                

@get("/")
def index():
    global n_objects
    return template("index.html",n_objects=n_objects)

@post("/cmd")
def cmd():
    #  print("按下了按钮: "+request.body.read().decode())
    global param1
    param = request.body.read().decode();
    print(param)
    if param == 'go':
        go()
        print("go")
    if param == 'back':
        back()
        print("back")
    if param == 'left':
        left()
        print("left")
    if param == 'right':
        right()
        print("right")
    if param == 'stop':
        stop()
        print("stop")
    if param == 'resume':
        param1=0
        go()
        go()
        go()
        print("resume object to 0")
    return "OK"

assets_path='./assets'

@route('/assets/<filename:re:.*\.css|.*\.js|.*\.png|.*\.jpg|.*\.gif>')
def server_static(filename):
    """定义/assets/下的静态(css,js,图片)资源路径"""
    return static_file(filename, root=assets_path)

@route('/<filename:re:.*\.css|.*\.js|.*\.png|.*\.jpg|.*\.gif>')
def server_static(filename):
    return static_file(filename, root='.')

@post("/object")
def object():
    #print("按下了按钮: "+request.body.read().decode())
    global param1
    param1 = int(request.body.read().decode());
    print(param1)      
    return "OK"

def run1():
    print('thread %s is running...' % threading.current_thread().name)
    run(host="0.0.0.0",port="8080")




def main():
    print('thread %s is running...' % threading.current_thread().name)
    t1=threading.Thread(target=loop_read)
    t2=threading.Thread(target=run1)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

if __name__=="__main__":
    main()