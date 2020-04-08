#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import signal
import sys
import l293d
import keyboard
import logging
import rover_constants as rc

# use Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BOARD)

# set GPIO input and output channels
GPIO.setup(rc.pinTrigger, GPIO.OUT)
GPIO.setup(rc.pinEcho, GPIO.IN)
GPIO.setup(rc.sensor, GPIO.IN)

# setup Motor pins
l293d.Config.pin_numbering = 'BOARD'
cases = (([rc.Motor1E, rc.Motor1A, rc.Motor1B], True), ([rc.Motor2E, rc.Motor2A, rc.Motor2B], True))
motors = []
for pins, force_selection in cases:
    motors.append(l293d.DC(*pins, force_selection=force_selection))

motor1 = motors[0]
motor2 = motors[1]


def close():
    logging.info("\nMain    : Turning off sensors and motors...\n")
    GPIO.cleanup()
    l293d.cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, close)


def set_rpm_start():
    rc.rpm_sample_start = time.time()


def set_rpm_end():
    rc.rpm_sample_end = time.time()


def get_rpm():
    if not rc.rpm_sample_count:
        set_rpm_start()
        rc.rpm_sample_count = rc.rpm_sample_count + 1
    else:
        rc.rpm_sample_count = rc.rpm_sample_count + 1

    if rc.rpm_sample_count == rc.rpm_samples_to_collect:
        set_rpm_end()
        delta = rc.rpm_sample_end - rc.rpm_sample_start
        delta = delta / 60
        rc.rpm = (rc.rpm_samples_to_collect / delta) / 2
        logging.debug("rpm      : RPM = %d", rc.rpm)
        rc.rpm_sample_count = 0
    else:
        logging.debug("rpm     : count is %d", rc.rpm)


GPIO.add_event_detect(rc.sensor, GPIO.RISING, callback=get_rpm)


def set_ds_start():
    # track the times
    rc.ds_sample_start = time.time()


def set_ds_end():
    rc.ds_sample_stop = time.time()
    # time difference between start and arrival
    elapsed_time = rc.ds_sample_stop - rc.ds_sample_start
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    rc.distance = (elapsed_time * 34300) / 2
    if rc.distance < 30:
        logging.info("Distance: %.1f cm", rc.distance)
    time.sleep(0.1)


GPIO.add_event_detect(rc.sensor, GPIO.FALLING, callback=set_ds_start)
GPIO.add_event_detect(rc.sensor, GPIO.RISING, callback=set_ds_end)


def thread_ds():
    logging.info("Distance: Started RPM sensor thread")
    # set Trigger to HIGH
    GPIO.output(rc.pinTrigger, True)
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(rc.pinTrigger, False)


def initialize_motors():
    logging.info("Motors  : Initializing motors sequence")
    # Run the motors so visible
    motor1.clockwise(duration=1)
    motor2.clockwise(duration=1)
    # Run the motors so visible
    motor1.anticlockwise(duration=1)
    motor2.anticlockwise(duration=1)
    # Spin right
    motor1.clockwise(duration=1)
    motor2.anticlockwise(duration=1)
    # Spin left
    motor1.anticlockwise(duration=1)
    motor2.clockwise(duration=1)


def thread_motors():
    logging.info("Motors  : Started motors thread")
    initialize_motors()
    try:
        if rc.key == "w":
            # move forward
            logging.info("Motors  : Moving forward")
            motor1.clockwise(duration=1)
            motor2.clockwise(duration=1)
        if rc.key == "a":
            # move left
            logging.info("Motors  : Turn left")
            motor1.anticlockwise(duration=1)
            motor2.clockwise(duration=1)
        if rc.key == "s":
            # move backward
            logging.info("Motors  : Moving backward")
            motor1.anticlockwise(duration=1)
            motor2.anticlockwise(duration=1)
        if rc.key == "d":
            # move right
            logging.info("Motors  : Turn right")
            motor1.clockwise(duration=1)
            motor2.anticlockwise(duration=1)
        if rc.key == "space":
            logging.info("Motors: Stop")
            motor1.stop(duration=1)
            motor2.stop(duration=1)
    except Exception:
        logging.error("Motors  : Exception found")


def thread_keys(keyEvent):
    rc.key = keyEvent.name
    if rc.key == "escape":
        exit(1)


if __name__ == "__main__":
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main    : Welcome to the RPM and Distance sensor")
    keyboard.on_press(thread_keys)
    try:
        while True:
            thread_motors()
            thread_ds()
    except KeyboardInterrupt:
        print(">>> Interrupted")
        print(">>> Quit")

    # Done
    logging.info("Main    : all done")
