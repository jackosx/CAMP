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

drumstick_id = config.id

# client = MQTTClient("drumstick-{}".format(config.id), "manatee.local")
# client.connect()

# See wiki for pinout: https://github.com/jackosx/CAMP/wiki/ESP32-Hardware

# TODO: Make high or low in config to support 2 sticks
stick = Accelerometer()
striking = False

g_thresh = config.threshold

# For debugging. Allows dev to adjust touch_thresh in REPL
def set_touch_thresh(new_thresh):
    global g_thresh
    g_thresh = new_thresh

# Called when new stick struck
def strike(stick=0, velocity=0):
    global striking
    print("STRIKE", velocity)
    striking = True
    # client.publish('i/d/{}/d/s/{}'.format(drumpad_id, 0), str(min(velocity, 127)))

# Read sesnors and update pads touched. Meant to be called frequently
def sample(verbose=False):
    global striking
    x, y, z = stick.get_accel()
    val = x*x + y*y + z*z
    if verbose:
        print("{:5.2f}  |  {:4.4f}, {:4.4f}, {:4.4f}".format(val, x, y, z))
    if val > config.threshold and not striking:
        strike(0, val * 2)
    elif val <= config.threshold and striking:
        striking = False
