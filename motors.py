import signal
import sys
import RPi.GPIO as GPIO
from time import sleep
import pyrebase
import json


config = {
  "apiKey": "AIzaSyDj3I3vvKVbWEVqCAxpfxNqQaMcv7t94cU",
  "authDomain": "mini-robot-rover.firebaseapp.com",
  "databaseURL": "https://mini-robot-rover.firebaseio.com",
  #"serviceAccount": "./google-services.json",
  "storageBucket": "mini-robot-rover.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

 
GPIO.setmode(GPIO.BOARD)
 
Motor1A = 33
Motor1B = 35
Motor1E = 37
 
Motor2A = 11
Motor2B = 13
Motor2E = 15

throttle = None
direction = None

def user_action_change_handler(action):
	event = action["event"]
	data = action["data"]
	path = action["path"]
	
	print("steam handler invoked: " % event)
	print("Data is: "% data)
	
	print(type(data))
	#throttle = data.get('throttle')
	#direction = data.get('direction')


firebase_stream = db.child("rover_status/mini").stream(user_action_change_handler)
data = db.child("rover_status/mini").get()


def close(signal, frame):
	if signal != 0:
		try:
			print("\nTurning off motors controller...\n")
			firebase_stream.close()
			GPIO.cleanup()
		except (RuntimeError, Exception):
			print("Failed to clean up")
			sys.exit(0)

	sys.exit(0)



def forward():
	print "Going forwards"
	GPIO.output(Motor1A,GPIO.HIGH)
	GPIO.output(Motor1B,GPIO.LOW)
	GPIO.output(Motor1E,GPIO.HIGH)
	 
	GPIO.output(Motor2A,GPIO.HIGH)
	GPIO.output(Motor2B,GPIO.LOW)
	GPIO.output(Motor2E,GPIO.HIGH)
	 
	sleep(0.5)

def backward():
	print "Going backwards"
	GPIO.output(Motor1A,GPIO.LOW)
	GPIO.output(Motor1B,GPIO.HIGH)
	GPIO.output(Motor1E,GPIO.HIGH)
	 
	GPIO.output(Motor2A,GPIO.LOW)
	GPIO.output(Motor2B,GPIO.HIGH)
	GPIO.output(Motor2E,GPIO.HIGH)
	 
	sleep(0.2)


def left():	
	print "Turn right once"
	GPIO.output(Motor2A,GPIO.HIGH)
	GPIO.output(Motor2B,GPIO.LOW)
	GPIO.output(Motor2E,GPIO.HIGH)
	
	GPIO.output(Motor1A,GPIO.LOW)
	GPIO.output(Motor1B,GPIO.HIGH)
	GPIO.output


def right():
	print "Turn right once"
	GPIO.output(Motor2A,GPIO.HIGH)
	GPIO.output(Motor2B,GPIO.LOW)
	GPIO.output(Motor2E,GPIO.HIGH)
	
	GPIO.output(Motor1A,GPIO.LOW)
	GPIO.output(Motor1B,GPIO.HIGH)
	GPIO.output(Motor1E,GPIO.HIGH)
	
	sleep(0.2) 


def stop():
	print "Now stop"
	GPIO.output(Motor1E,GPIO.LOW)
	GPIO.output(Motor2E,GPIO.LOW)


def init():
	forward()
	backward()
	left()
	right()
	stop()
	sleep(2)


# start
signal.signal(signal.SIGINT, close)

#setup inputs
GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)
GPIO.setup(Motor1E,GPIO.OUT)
 
GPIO.setup(Motor2A,GPIO.OUT)
GPIO.setup(Motor2B,GPIO.OUT)
GPIO.setup(Motor2E,GPIO.OUT)


# create an infinte loop to keep the script running
init()
try:
    while True:
		if direction == "left":
			left()
		if direction == "right":
			right()
		if throttle == "forward":
			forward()
		if throttle == "reverse":
			backward()
		sleep(0.001)
		
except KeyboardInterrupt:
    print ("Quit")
    raise
except Exception, e:
	print(e)
	sys.exit(0)
