#!/usr/bin/python

import RPi.GPIO as GPIO
import pyrebase
import time
import sys
import signal

# define the GPIO pin our sensor is attached to
sensor = 14

# sensor variables
sample = 10 # how many half revolutions to time
count = 0
start = 0
end = 0


# Close handler
def close(signal, frame):
    if signal != 0:
        try:
            print("\nStopping RPM sensor...\n")
            GPIO.cleanup()
            print("GPIO removed")
            sys.exit(0)
        except SystemExit:
            print("sys.exit() worked as expected")
        except:
            print(sys.exc_info()[0])
            print("Failed to clean up")
        else:
            print("Exit with signal=" + str(signal))

    sys.exit(1)

signal.signal(signal.SIGINT, close)


# Firebase variables
config = {
  "apiKey": "AIzaSyDj3I3vvKVbWEVqCAxpfxNqQaMcv7t94cU",
  "authDomain": "mini-robot-rover.firebaseapp.com",
  "databaseURL": "https://mini-robot-rover.firebaseio.com",
  "storageBucket": "mini-robot-rover.appspot.com"
}
firebase = pyrebase.initialize_app(config)
firebase_db = firebase.database()

# RPM sensor calcuations
def set_start():
    global start
    start = time.time()


def set_end():
    global end
    end = time.time()


def get_rpm(c):
    global count # declare the count variable global so we can edit it

    if not count:
        set_start() # create start time
        count = count + 1 # increase counter by 1
    else:
        count = count + 1

    if count==sample:
        set_end() # create end time
        delta = end - start # time taken to do a half rotation in seconds
        delta = delta / 60 # converted to minutes
        rpm = (sample / delta) / 2 # converted to time for a full single rotation
        print ("\nRPM is: " + str(rpm))
        sys.stdout.flush()
        firebase_db.child("rpm").set(rpm)
        count = 0 # reset the count to 0
    else:
        print ("\r>>Count is %d" % count),
        sys.stdout.flush()


def setup_pins():
    GPIO.setmode(GPIO.BCM) # set GPIO numbering system to BCM
    GPIO.setup(sensor,GPIO.IN) # set our sensor pin to an input
    GPIO.add_event_detect(sensor, GPIO.RISING, callback=get_rpm) # execute the get_rpm function when a HIGH signal is detected

try:
    print ("Tracking 'rpm'")
    setup_pins()

    while True: # create an infinte loop to keep the script running
        time.sleep(0.1)
except KeyboardInterrupt:
    print ("Quit")
    raise
except Exception, e:
	print(e)
	sys.exit(1)
