import signal
import sys
import RPi.GPIO as GPIO
from time import sleep
import pyrebase
import json


data = {}
with open('google-services.json') as f:
  data = json.load(f)
  
config = {
  "apiKey": data["client"][0]["api_key"]["current_key"],
  "authDomain": data["project_info"]["firebase_url"],
  "storageBucket": data["project_info"]["storage_bucket"],
  "serviceAccount": "./google-services.json"
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


def close(signal, frame):
    print("\nTurning off motors controller...\n")
    GPIO.cleanup() 
    sys.exit(0)


def user_action_change_handler(action):
	print(str(action))


db.child("user_action").child(user['idToken']).stream(user_action_handler)


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
	 
	sleep(2)


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


def run():
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
try:
    while True:
        run()
except KeyboardInterrupt:
    print ("Quit")
    GPIO.cleanup()

