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
stick = Accelerometer(scl=config.accel_scl, sda=config.accel_sda)

buzz = machine.Pin(config.buzz_pin, machine.Pin.OUT)
buzz.value(0)

striking = False

g_thresh = config.threshold

queue_len = 100
strike_avg = RollingStats(10, 10)

debounce_count = 0
buzz_count = 0
led_count = 0 # TODO for LEDs on strike

prev_x, prev_y, prev_z = 0, 0, 0
prev_dx, prev_dy, prev_dz = 0, 0, 0

def calc_velocity(val):
    width = config.max_strike_scale - config.min_strike_scale
    floored = max(20, val - config.min_strike_scale) / width * 127
    return min(127, floored)

# Re-up all countdown counters after a strike
def refill_counters(velocity=80):
    global debounce_count, buzz_count, led_count
    debounce_count = config.debounce_ms // config.sample_frequency
    buzz_ms = (velocity / 127) * (config.buzz_ms_max - config.buzz_ms_min) \
                    + config.buzz_ms_min
    buzz_count = buzz_ms // config.sample_frequency

def decrement_counters():
    global debounce_count, buzz_count
    if debounce_count > 0: # If post strike, in debounce period
        debounce_count -= 1
    if buzz_count > 0:
        buzz_count -= 1
        if buzz_count == 0:
            buzz.value(0) # Stop buzzing

# For debugging. Allows dev to adjust touch_thresh in REPL
def set_touch_thresh(new_thresh):
    global g_thresh
    g_thresh = new_thresh

# Called when new stick struck
def strike(stick=0, unscaled=0):
    global striking
    striking = True
    refill_counters()
    buzz.value(1) # Start haptic
    velocity = calc_velocity(unscaled)
    strike_avg.update(velocity)
    print("STRIKE {:5.0f} VEL: {:5.0f}".format(unscaled, velocity))
    print("AVG{:5.0f}".format(strike_avg.avg))
    buzz.value(1) # Start haptic (sometimes it doesn't)

    # client.publish('i/d/{}/d/s/{}'.format(drumpad_id, 0), str(min(velocity, 127)))

# Read sesnors and update pads touched. Meant to be called frequently
def sample(verbose=False):
    global striking
    global prev_x, prev_y, prev_z
    global prev_dx, prev_dy, prev_dz

    x, y, z = stick.get_accel() # Positive y is moving down
    dx, dy, dz = (x - prev_x), (y - prev_y), (z - prev_z) # Negative dy is bottom of swing?
    ddx, ddy, ddz = (dx - prev_dx), (dy - prev_dy), (dz - prev_dz)
    # val = (dx*dx + dy*dy + dz*dz) ** config.power
    # val = (dy*dy) ** config.power

    val = (y*y) ** config.power
    if config.use_jerk is True:
        val = (dy*dy) ** config.power

    # print("================================{:5.0f}".format(val))
    if val > config.print_threshold:
        print("{:5.2f}  |  {:4.4f}, {:4.4f}, {:4.4f}".format(val, ddy, dy, y))
    if val > config.threshold and dy < 0 and not striking and debounce_count == 0:
        print("{:5.2f}  |  {:4.4f}, {:4.4f}, {:4.4f}".format(val, ddy, dy, y))
        print("================================", y)
        strike(0, y)
    elif val <= config.threshold and striking:
        striking = False
    prev_x, prev_y, prev_z = x, y, z
    prev_dx, prev_dy, prev_dz = dx, dy, dz
    decrement_counters()
