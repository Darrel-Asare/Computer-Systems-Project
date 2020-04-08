# set GPIO Pins
pinTrigger = 7
pinEcho = 19
sensor = 8

# motors
Motor1A = 33
Motor1B = 35
Motor1E = 37

Motor2A = 11
Motor2B = 13
Motor2E = 15

# Counter variables
rpm_samples_to_collect = 10 # how many half revolutions to time
rpm_sample_count = 0
rpm_sample_start = 0
rpm_sample_end = 0
rpm = 0

ds_sample_start = 0
ds_sample_stop = 0
distance = float('Inf')

useKeys = False
key = None
