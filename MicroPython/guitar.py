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
import mannet
import config
import touchpad
import time

guitar_id = config.id
stdev_trigger = config.stdev_trigger

# See wiki for pinout: https://github.com/jackosx/CAMP/wiki/ESP32-Hardware
# For skinnier board see printout it shipped with
fret_sensors = [touchpad.TouchPad(p, stdev_trigger) for p in config.fret_pins]
strum_sensor = touchpad.TouchPad(config.strum_pins[0], stdev_trigger) # eventually more pins will be used for strumming

touch_thresh = config.threshold
strum_thresh = config.strum_threshold

active_fret = 0
strumming = False

def calibrate():
    for i in range(400):
        time.sleep_ms(config.sample_frequency)
        strum_sensor.calibrate_step()
        for s in fret_sensors:
            s.calibrate_step()


def set_touch_thresh(new_thresh):
    global touch_thresh
    touch_thresh = new_thresh

# Called when the active fret changes, sends MQTT message
def update_fret(new_fret):
    print("NEW FRET",  new_fret)
    global active_fret
    active_fret = new_fret
    mannet.send_message('i/g/{}/d/f'.format(guitar_id), str(active_fret))

# Called when strum detected, sends MQTT message
def strum(velocity):
    global strumming
    strumming = True
    v = min(int(round(velocity*config.velocity_scale)), 127)
    mannet.send_message('i/g/{}/d/s'.format(guitar_id), str(v))
    print("STRUM", v)

# Read sensors, update fret touched and loof for strum.
# To be called frequently.
def sample(verbose=False):
    global strumming
    max_zstat  = 0
    best_fret = 0 # Default to no fret touched
    for i, t in enumerate(fret_sensors):
        zstat = t.read()
        abov_thresh = zstat - stdev_trigger
        if verbose:
            print(i, zstat)
        if zstat >  stdev_trigger:
            max_zstat = zstat
            best_fret = i + 1
    if best_fret != active_fret:
        update_fret(best_fret)
    strum_zstat = strum_sensor.read()
    strum_diff = stdev_trigger - strum_zstat
    if verbose:
        print("Strum:", strum_zstat)
    if strum_zstat > stdev_trigger and strumming is False:
        strum(strum_zstat)
    elif strumming is True and strum_zstat <= stdev_trigger:
        strumming = False
