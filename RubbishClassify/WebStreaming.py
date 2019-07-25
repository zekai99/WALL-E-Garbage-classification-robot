from __future__ import print_function
import signal
import sys
import tty
import termios
import os
from picamera import PiCamera, Color
from time import sleep
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import time, threading
import fcntl
from PIL import Image

stream=io.BytesIO()
camera=picamera.PiCamera(resolution='640x480', framerate=24)

def emergency(signal, frame):
    print('Something went wrong!')
    sys.exit(0)

signal.signal(signal.SIGINT, emergency)

PAGE="""\
<html>
<head>
<title>SWS3009 PiCamera Peek-a-boo</title>
</head>
<body>
<img src="stream.mjpg" width="320" height="240" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)
    
output = StreamingOutput()
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def emergency(signal, frame):
    print('Something went wrong!')
    sys.exit(0)

def web_server():
    print('thread %s is running...' % threading.current_thread().name)

    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
        
def predict():
    global stream
    print('thread %s is running...' % threading.current_thread().name)
    time.sleep(5)
    while True:
        camera.capture('snapshot1.jpg', use_video_port=True)
        with open('snapshot1.jpg', 'rb') as ff:
            data = ff.read()
        try:
            f = open('snapshot.jpg', 'wb')
            fcntl.flock(f, fcntl.LOCK_EX)
            #image = Image.open(stream)
            #image.save("snapshot.jpg")
            f.write(data)
            fcntl.flock(f, fcntl.LOCK_UN)
            print("capture")
        finally:
            if f:
                f.close()
        time.sleep(2)
    #for filename in camera.capture_continuous('snapshot.jpg'):
        #print('Capture%s' % filename)
        #time.sleep(5)

def main():
    #demoCamera.resolution=(500,480)
    #demoCamera.start_preview()
    print('thread %s is running...' % threading.current_thread().name)
    t1=threading.Thread(target=web_server)
    t2=threading.Thread(target=predict)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

if __name__=="__main__":
    main()
    