#!/usr/bin/python

from picamera import PiCamera
from gpiozero import MotionSensor
from time import *
import RPi.GPIO as GPIO
import datetime
import os

PIRPin = 4

def readMotion(pin):
    m = GPIO.input(pin)
    return m == 1

def cleanStaleFiles(folder):
    for dirpath, dirnames, filenames in os.walk(folder):
        for filename in filenames:
            curpath = os.path.join(folder, filename)
            mod = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
            if datetime.datetime.now() - mod > datetime.timedelta(minutes=60):
                os.remove(curpath)


GPIO.setmode(GPIO.BCM)
GPIO.setup(PIRPin, GPIO.IN)

camera = PiCamera()

camera.resolution = (2592, 1944)
camera.framerate = 15
i = 0
sleep(5)
print("Starting detection")

while True:
    if readMotion(PIRPin):
        i+=1
        for j in range(1,4):
            filePath = '/home/pi/Desktop/Camera/image{}_{}.jpg'.format(i, j)
            print("Capturing %s" % filePath)
            camera.capture(filePath)
        cleanStaleFiles('/home/pi/Desktop/Camera/')

        sleep(10)
        
#camera.start_preview(alpha=200)
#camera.exposure_mode = 'beach'
#sleep(10)
#camera.stop_preview()

