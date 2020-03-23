import RPi.GPIO as GPIO
import pyrebase
import time
import signal
import sys


# set GPIO Pins
pinTrigger = 7
pinEcho = 19


# Close handler
def close(signal, frame):
    if signal != 0:
        try:
            print("\nTurning off ultrasonic distance detection...\n")
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

# set GPIO input and output channels
def setup_pins():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pinTrigger, GPIO.OUT)
    GPIO.setup(pinEcho, GPIO.IN)

try:
    print ("Tracking distance in 'cm'")
    setup_pins()

    while True:
        # set Trigger to HIGH
        GPIO.output(pinTrigger, True)
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(pinTrigger, False)

        startTime = time.time()
        stopTime = time.time()

        # save start time
        while 0 == GPIO.input(pinEcho):
            startTime = time.time()

        # save time of arrival
        while 1 == GPIO.input(pinEcho):
            stopTime = time.time()

        # time difference between start and arrival
        TimeElapsed = stopTime - startTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2

        if distance <  50:
            print ("\rDistance: %.1f cm" % distance),
            sys.stdout.flush()
            firebase_db.child("distance").set(distance)

        time.sleep(1)
	
except KeyboardInterrupt:
    print ("Quit")
    raise
except Exception, e:
	print(e)
	sys.exit(1)
