#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Abhinaba Basu
# Extended to 

import sys
import urllib2
import requests
import Adafruit_DHT
import RPi.GPIO as GPIO
import json
import time
import datetime

url = "http://192.168.1.42/api/Thing"

def registerDevice(deviceId):
    jsonDeviceStr = """
    {{
        "Id": "{}",
        "Description": "RPi Magic Mirror, Python client",
        "Capability": [
            "temp",
            "humidity",
            "motion"
        ]
    }}
    """

    # register the device with ThingServer
    print("Registering device with ")
    jsonDevice = jsonDeviceStr.format(deviceId)
    print(jsonDevice)

    headers = {'Content-type': 'application/json'}
    r = requests.put(url, data=jsonDevice, headers=headers)

    print("Got response {}".format(r.status_code))

    if(r.status_code != 200):
        print("Failed to register device with status %d" %(r.status_code))
        return ""

    # Need to parse r.text to get teh token
    rJson = json.loads(r.text)
    token = rJson["id"]
    print("Successfully registered device and got AccessToken %s" % token);

    return token

def sendData(url, deviceId, token, temperature, humidity, motion):
    jsonDataStr = """
    {{
        "Id": "{}",
        "TimeStamp": {},
        "Data" : [
            {{
                "Name": "temperature",
                "Value": "{}"
            }},
            {{
                "Name": "humidity",
                "Value": "{}"
            }},
            {{
                "Name": "motion",
                "Value": "{}"
            }}

        ]
    }}
    """
    formattedStr = jsonDataStr.format(deviceId, time.time() * 1000, temperature, humidity, motion)

    print('Sending {0} Temp={1:0.1f}*  Humidity={2:0.1f}% Motion={3}'.format(datetime.datetime.now(), temperature, humidity, motion))
    headers = {'Content-type': 'application/json', 'AccessToken' : token}
    r = requests.post(url, data=formattedStr, headers=headers)
    statusCode = r.status_code
    print("Got response {}".format(statusCode))

    if(statusCode == 404 or statusCode == 401):
        # Failed with unknown device, reattempt registering
        token = registerDevice(deviceId)
        if token:
            r = requests.post(url, data=formattedStr, headers=headers)
            print("Re-attempt got response {}", r.status_code)
        else:
            print("Failed to register as well, giving up on data send")

# returns True is motion is detected
def readMotion(pin):
    m = GPIO.input(pin)
    return m == 1

def readSensor(sensor, pin):
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return humidity, temperature

# =================================================================================================================
# Parse command line parameters.
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }
if len(sys.argv) == 5 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    sensorPin = sys.argv[2]
    PIRPin = int(sys.argv[3])
    deviceId = sys.argv[4]
else:
    print('usage: ./Adafruit_DHT.py [11|22|2302] SensorGPIOpin# PIRGPIOpin# deviceId')
    print('example: ./Adafruit_DHT.py 11 3 4 b1d943ce-725d-4fe4-97b3-c868032df95f - Read from a DHT11 connected to GPIO #3 and PIR sensor to #4')
    sys.exit(1)

# =================================================================================================================
# Initial setup device and initial reaidings
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIRPin, GPIO.IN)

token = registerDevice(deviceId)
motion = False
humidity, temperature = readSensor(sensor, sensorPin)
print('Initial Reading Temp={0:0.1f}*  Humidity={1:0.1f}% Motion={2}'.format(temperature, humidity, motion))
lastHumidity = humidity
lastTemp = temperature


# =================================================================================================================
# Loop to read and push data
lastMotionTime = 0.0
lastSensorTime = 0.0

while True:

    currTime = time.time()

    # Check for motion very often and once you find it do not check for a few secs
    motion = readMotion(PIRPin)
    if (motion and (currTime - lastMotionTime >= 10.0)):
        statusCode = sendData(url, deviceId, token, temperature, humidity, motion)
        lastMotionTime = currTime
        continue

    # Check sensor every 60 seconds
    if(currTime - lastSensorTime) > 10:
        for i in range(0,5):
            humidity, temperature = readSensor(sensor, sensorPin)

            # sometimes weird data comes, reject if data varies from last a lot and retake data
            if( humidity is not None and temperature is not None and  humidity < 110 and (abs(humidity-lastHumidity)/lastHumidity)< 0.3) and ((abs(temperature - lastTemp)/lastTemp) < 0.3):
                break

            print("Wide change in data {} {}, retake".format(temperature, humidity))

        lastHumidity = humidity
        lastTemp = temperature

        # Un-comment the line below to convert the temperature to Fahrenheit.
        #temperature = temperature * 9/5.0 + 32

        statusCode = sendData(url, deviceId, token, temperature, humidity, motion)
        lastSensorTime = time.time()

    time.sleep(0.01)

