# A simple MicroPython Module for controlling LEDs
# Functions include:
#   leds.all_on()
#   leds.all_off()
#   leds.show_success()
#   leds.show_failure()

import machine
import time

red_pin   = 15
green_pin = 16

red   = machine.Pin(red_pin, machine.Pin.OUT)
green = maching.Pin(green_pin, machine.Pin.OUT)

leds = [red, green]

# Turn all LEDs on
def all_on():
    for l in leds:
        l.high()

# Turn all LEDs off
def all_off():
    for l in leds:
        l.low()

# Turn red off and green on
def show_success():
    red.low()
    green.high()

# Turn green off and red on
def show_failure():
    red.high()
    green.low()

def blink_all(secs):
    all_on()
    time.sleep(secs/2)
    all_off()
    time.sleep(secs/2)
