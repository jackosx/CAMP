# ESP32 MicroPython Guitar/Bass instrument.
# Module for creating broom instrument.
# Guitar/Bass differences implemented on backend.
#
# Example config.py:
#
# instrument_type = 'guitar'
#
# id = 0
#
# fret_pins = [4, 32, 15, 13]
#
# strum_pins = [12]
#
# threshold = 200
#
# strum_threshold = 350
#
# # Milliseconds between readings
# sample_frequency = 15
#
# # Development mode. False means start read loop at boot
# dev = False


import machine
from umqtt.simple import MQTTClient
import config

guitar_id = config.id

client = MQTTClient("guitar-{}".format(config.id), "manatee.local")
client.connect()

# See wiki for pinout: https://github.com/jackosx/CAMP/wiki/ESP32-Hardware
# For skinnier board see printout it shipped with
fret_sensors = [machine.TouchPad(machine.Pin(p)) for p in config.fret_pins]
strum_sensor = machine.TouchPad(machine.Pin(config.strum_pins[0])) # eventually more pins will be used for strumming

touch_thresh = config.threshold
strum_thresh = config.strum_threshold

active_fret = 0
strumming = False

def set_touch_thresh(new_thresh):
    global touch_thresh
    touch_thresh = new_thresh

# Called when the active fret changes, sends MQTT message
def update_fret(new_fret):
    print("NEW FRET",  new_fret)
    global active_fret
    active_fret = new_fret
    client.publish('i/g/{}/d/f'.format(guitar_id), str(active_fret))

# Called when strum detected, sends MQTT message
def strum(velocity):
    global strumming
    strumming = True
    client.publish('i/g/{}/d/s'.format(guitar_id), str(min(velocity, 127)))
    print("STRUM")

# Read sensors, update fret touched and loof for strum.
# To be called frequently.
def sample(verbose=False):
    global strumming
    max_diff  = 0
    best_fret = 0 # Default to no fret touched
    for i, t in enumerate(fret_sensors):
        cap_val = t.read()
        cap_diff = touch_thresh - cap_val
        if verbose:
            print(i, cap_val)
        if cap_diff >  max_diff:
            max_diff = cap_diff
            best_fret = i + 1
    if best_fret != active_fret:
        update_fret(best_fret)
    strum_val = strum_sensor.read()
    strum_diff = strum_thresh - strum_val
    if verbose:
        print("Strum:", strum_val)
    if strum_diff > 0 and strumming is False:
        strum(strum_diff)
    elif strumming is True and strum_diff <= 0:
        strumming = False
