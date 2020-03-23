import signal
import sys
import RPi.GPIO as GPIO
from time import sleep
import pyrebase
import json


Motors_Enabled = True
Motor1A = 33
Motor1B = 35
Motor1E = 37
 
Motor2A = 11
Motor2B = 13
Motor2E = 15

throttle = None
direction = None


# Close handler
def close(signal, frame):
	if signal != 0:
		try:
			print("\nStopping stream and turning off motors controller...\n")
			# TODO: update in rpi: https://gist.github.com/codeAshu/f6384203706e989b0d38db6e0a9d11e7
			if firebase_stream is not None:
				firebase_stream.close()
				print("Stream closed")
			else:
				print("No stream found")
			if Motors_Enabled:
				GPIO.cleanup()
				print("GPIO removed")
			else:
				print("GPIO not enabled")
			
			sys.exit(0)
		except SystemExit:
			print("sys.exit() worked as expected")
		except:
			print(sys.exc_info()[0])
			print("Failed to clean up")

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
firebase_stream = None


def user_action_change_handler(action):
	global throttle, direction

	event = action["event"]
	data = action["data"]
	path = action["path"]
	
	print(">> Stream handler invoked: " + event)
	print("Body of request: " + str(action))
	print("Data is: '" + str(data) + "' path is: '" + path + "' and type is: " + str(type(data)))
	
	if isinstance(data, dict):
		throttle = data.get('throttle')
		direction = data.get('direction')
	elif isinstance(data, (str, int, unicode)):
		if path == "/throttle":
			throttle = data
		elif path == "/direction":
			direction = data
		else:
			print("Unsupported path found: " + path + " with data: " + str(data))
	else:
		print("Unsupported event type: " + event)

	print(">> Throttle = " + throttle + ", Direction = " + direction)


# Motor controls
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

# motor initialization sequence
def init():
	forward()
	backward()
	left()
	right()
	stop()
	sleep(2)


#setup inputs
def setup_pins():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(Motor1A,GPIO.OUT)
	GPIO.setup(Motor1B,GPIO.OUT)
	GPIO.setup(Motor1E,GPIO.OUT)
	
	GPIO.setup(Motor2A,GPIO.OUT)
	GPIO.setup(Motor2B,GPIO.OUT)
	GPIO.setup(Motor2E,GPIO.OUT)


# start
# create an infinte loop to keep the script running
try:
	if Motors_Enabled:
		setup_pins()
		init()

	firebase_stream = firebase_db.child("rover_status/mini").stream(user_action_change_handler)
	
	while True:
		if Motors_Enabled:
			if direction == "left":
				left()
			elif direction == "right":
				right()
			elif throttle == "forward":
				forward()
			elif throttle == "reverse":
				backward()
			else:
				stop()

		sleep(0.001)
		
except KeyboardInterrupt:
    print ("Quit")
    raise
except Exception, e:
	print(e)
	sys.exit(1)
