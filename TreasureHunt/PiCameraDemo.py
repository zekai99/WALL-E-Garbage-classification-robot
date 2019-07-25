import signal
import sys

from picamera import PiCamera, Color
from time import sleep

#######################################
#Allow Ctrl-C in case something locks the screen
#######################################

def emergency(signal, frame):
    print('Something went wrong!')
    sys.exit(0)

signal.signal(signal.SIGINT, emergency)

#######################################
#Initialization
#######################################

demoCamera = PiCamera()


#######################################
#Simple Preview
#######################################

#demoCamera.start_preview()
#sleep(5)
#demoCamera.stop_preview()


########################################
#Rotation
########################################

#demoCamera.rotation = 180
#demoCamera.start_preview()
#sleep(10)
#demoCamera.stop_preview()


########################################
#Take picture
########################################

#demoCamera.start_preview()
#sleep(5)
#demoCamera.capture('/home/pi/Desktop/sample.jpg')
#demoCamera.stop_preview()


########################################
#Record Video
#Can use omxplayer on RPi to play
########################################

#demoCamera.start_preview()
#demoCamera.start_recording('/home/pi/Desktop/sampleVideo.h264')
#sleep(5)
#demoCamera.stop_recording()
#demoCamera.stop_preview()

########################################
#Annotation
########################################

demoCamera.start_preview()
demoCamera.annotate_background = Color('white')
demoCamera.annotate_foreground = Color('red')
demoCamera.annotate_text = " SWS3009B - 2019"
sleep(5)
demoCamera.capture('/home/pi/Desktop/classPhoto.jpg')
demoCamera.stop_preview()

