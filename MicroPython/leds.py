# A simple MicroPython Module for controlling LEDs
# Functions include:
#   leds.all_on()
#   leds.all_off()
#   leds.show_success()
#   leds.show_failure()

import machine
import time

red_pin   = 16
green_pin = 17

red   = machine.Pin(red_pin, machine.Pin.OUT)
green = machine.Pin(green_pin, machine.Pin.OUT)

leds = [red, green]

# Turn all LEDs on
def all_on():
    for l in leds:
        l.value(1)

# Turn all LEDs off
def all_off():
    for l in leds:
        l.value(0)

# Turn red off and green on
def show_success():
    red.value(0)
    green.value(1)

# Turn green off and red on
def show_failure():
    red.value(1)
    green.value(0)

def blink_all(secs):
    all_on()
    time.sleep(secs/2)
    all_off()
    time.sleep(secs/2)
