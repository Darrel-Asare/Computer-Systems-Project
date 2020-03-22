#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import signal
import sys
import l293d.driver as l293d
import logging
import threading
import rover_constants as rc

stopThreads = False
useKeys = False
key = None

# use Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BOARD)


# set GPIO input and output channels
GPIO.setup(rc.pinTrigger, GPIO.OUT)
GPIO.setup(rc.pinEcho, GPIO.IN)
GPIO.setup(rc.sensor, GPIO.IN)

# setup Motor pins
motor1 = l293d.motor(rc.Motor1E, rc.Motor1A, rc.Motor1B)
motor2 = l293d.motor(rc.Motor2E, rc.Motor2A, rc.Motor2B)



def close():
    global stopThreads

    logging.info("\nMain    : Turning off sensors and motors...\n")

    stopThreads = True
    GPIO.cleanup()
    l293d.cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, close)


def set_start():
    global start
    start = time.time()


def set_end():
    global end
    end = time.time()


def get_rpm():
    global count

    if not count:
        set_start()
        count = count + 1
    else:
        count = count + 1

    if count == rc.sample:
        set_end()
        delta = end - start
        delta = delta / 60
        rpm = (rc.sample / delta) / 2
        print(rpm)
        count = 0
    else:
        logging.info("rpm     : count is %d", count)


GPIO.add_event_detect(rc.sensor, GPIO.RISING, callback=get_rpm)


def thread_ds():
    logging.info("Distance: Started RPM sensor thread")
    while not stopThreads:
        # set Trigger to HIGH
        GPIO.output(rc.pinTrigger, True)
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(rc.pinTrigger, False)

        # track the times
        start_time = time.time()
        stop_time = time.time()

        # save start time
        while (0 == GPIO.input(rc.pinEcho)) and not stopThreads:
            start_time = time.time()

        # save time of arrival
        while (1 == GPIO.input(rc.pinEcho)) and not stopThreads:
            stop_time = time.time()

        # time difference between start and arrival
        elapsed_time = stop_time - start_time
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (elapsed_time * 34300) / 2

        logging.info("Distance: %.1f cm", distance)
        time.sleep(0.1)


def thread_rpm():
    logging.info("rpm     : Started RPM sensor thread")
    while not stopThreads:
        time.sleep(0.1)


def initialize_motors():
    logging.info("Motors  : Initializing motors sequence")
    # Run the motors so visible
    for i in range(0, 150):
        motor1.clockwise()
    # Run the motors so visible
    for i in range(0, 150):
        motor2.clockwise()
    # Run the motors so visible
    for i in range(0, 150):
        motor1.anticlockwise()
        motor2.anticlockwise()


def thread_motors():
    logging.info("Motors  : Started motors thread")
    initialize_motors()
    while not stopThreads:
        if key == "w":
            # move forward
            logging.info("Motors  : Moving forward")
            motor1.clockwise()
            motor2.clockwise()
        if key == "a":
            # move left
            logging.info("Motors  : Turn left")
            motor1.anticlockwise()
            motor2.clockwise()
        if key == "s":
            # move backward
            logging.info("Motors  : Moving backward")
            motor1.anticlockwise()
            motor2.anticlockwise()
        if key == "d":
            # move right
            logging.info("Motors  : Turn right")
            motor1.clockwise()
            motor2.anticlockwise()
        if key == "space":
            logging.info("Motors: Stop")
            motor1.stop()
            motor2.stop()


def thread_keys():
    global key
    while useKeys and not stopThreads:
        key = input().lower()


def thread_start(name):
    logging.info("Thread '%s': starting", name)
    if name == "rpm":
        thread_rpm()
    elif name == "ds":
        thread_ds()
    elif name == "motors":
        thread_motors()

    logging.info("Thread '%s': finishing", name)


if __name__ == "__main__":
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main    : Welcome to the RPM, Distance and Motor Rover")
    logging.info('Main    : Number of arguments:', len(sys.argv), 'arguments.')
    logging.info('Main    : Argument List:', str(sys.argv))
    useKeys = (sys.argv[1] == "useKeys")

    if useKeys:
        logging.info("Main    : Use 'W A S D' (move) and '<Space Bar>' (stop) to control the rover!")

    threads = list()
    rpmThread = threading.Thread(target=thread_rpm, args=("rpm",))
    threads.append(rpmThread)
    dsThread = threading.Thread(target=thread_ds, args=("ds",))
    threads.append(dsThread)
    motorThreads = threading.Thread(target=thread_motors, args=("motors",))
    threads.append(motorThreads)
    if useKeys:
        threads.append(threading.Thread(target=thread_keys, args=("keys",)))

    try:
        # start the threads
        for index in range(4):
            threads[index].start()

        # join the threads
        for index, thread in enumerate(threads):
            logging.info("Main    : before joining thread %d.", index)
            thread.join()
            logging.info("Main    : thread %d done", index)
    except KeyboardInterrupt:
        stopThreads = True
        print(">>> Quit")

    # Done
    logging.info("Main    : all done")
