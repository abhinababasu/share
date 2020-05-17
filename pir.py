#!/usr/bin/python

from gpiozero import MotionSensor
from time import *
pir = MotionSensor(4)

i = 0
while True:
    if pir.motion_detected:
        i+=1
        print("%d Motion!!!!!" % i)
        sleep(1)
