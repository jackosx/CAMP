# ESP32 MicroPython Drumpad instrument
# Module for creating tappable capacitive drum pads
#
# Example config.py:
#
# instrument_type = 'drumpad'
#
# id = 0
#
# pad_pins = [4, 32, 15, 13]
#
# threshold = 600
#
# # Milliseconds between readings
# sample_frequency = 10
#
# # Development mode. False means start read loop at boot
# dev = True


import machine
from umqtt.simple import MQTTClient
from accelerometer import Accelerometer
import config
import array
from rollingaverage import RollingStats

drumstick_id = config.id

# client = MQTTClient("drumstick-{}".format(config.id), "manatee.local")
# client.connect()

# See wiki for pinout: https://github.com/jackosx/CAMP/wiki/ESP32-Hardware

# TODO: Make high or low in config to support 2 sticks
stick = Accelerometer()
striking = False

g_thresh = config.threshold

queue_len = 100
hit_queue = array.array("H", [0] * queue_len)
hit_idx = 0
hit_count = 0
strike_avg = RollingStats(10, 10)
debounce_count = 0

prev_x, prev_y, prev_z = 0, 0, 0

# For debugging. Allows dev to adjust touch_thresh in REPL
def set_touch_thresh(new_thresh):
    global g_thresh
    g_thresh = new_thresh

# Called when new stick struck
def strike(stick=0, velocity=0):
    global striking
    global debounce_count
    print("STRIKE {:5.0f}".format(velocity))
    striking = True
    debounce_count = config.debounce_samples
    strike_avg.update(velocity)
    print("AVG{:5.0f}".format(strike_avg.avg))
    # client.publish('i/d/{}/d/s/{}'.format(drumpad_id, 0), str(min(velocity, 127)))

# Read sesnors and update pads touched. Meant to be called frequently
def sample(verbose=False):
    global striking
    global hit_idx
    global hit_queue
    global hit_count
    global queue_len
    global prev_x, prev_y, prev_z
    global debounce_count

    x, y, z = stick.get_accel()
    dx, dy, dz = (x - prev_x), (y - prev_y), (z - prev_z)
    val = (dx*dx + dy*dy + dz*dz) ** config.power
    val = (dy*dy) ** config.power

    # print("================================{:5.0f}".format(val))
    # if verbose:
    print("{:5.2f}  |  {:4.4f}, {:4.4f}, {:4.4f}".format(val, dx, dy, dz))
    if val > config.threshold and not striking and debounce_count == 0:
        print("{:5.2f}  |  {:4.4f}, {:4.4f}, {:4.4f}".format(val, x, y, z))
        print("================================", val)
        strike(0, val)
        if (not hit_queue[hit_idx % queue_len]):
            hit_count += 1
            hit_queue[hit_idx % queue_len] = 1
    elif val <= config.threshold and striking:
        striking = False
        if (hit_queue[hit_idx % queue_len]):
            hit_count -= 1
            hit_queue[hit_idx % queue_len] = 0
    else:
        if (hit_queue[hit_idx % queue_len]):
            hit_count -= 1
            hit_queue[hit_idx % queue_len] = 0
    queue_time = queue_len * config.sample_frequency
    bpm = (hit_count / queue_time) * 60000
    # print("==============================   ", bpm)
    hit_idx += 1
    prev_x, prev_y, prev_z = x, y, z
    if debounce_count > 0:
        debounce_count -= 1
