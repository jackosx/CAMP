import machine
from umqtt.simple import MQTTClient

client = MQTTClient("guitar", "manatee.local")
client.connect()

# See wiki for pinout: https://github.com/jackosx/CAMP/wiki/ESP32-Hardware
touch_D4  = machine.TouchPad(machine.Pin(4))
touch_D32 = machine.TouchPad(machine.Pin(32))
touch_D15 = machine.TouchPad(machine.Pin(15))
touch_D13 = machine.TouchPad(machine.Pin(13))
touch_D12 = machine.TouchPad(machine.Pin(12))

fret_sensors = [touch_D4, touch_D32, touch_D13, touch_D15]
strum_sensor = touch_D12

touch_thresh = 600

active_fret = 0
strumming = False

def set_touch_thresh(new_thresh):
    global touch_thresh
    touch_thresh = new_thresh

def update_fret(new_fret):
    print("NEW FRET",  new_fret)
    global active_fret
    active_fret = new_fret
    client.publish('i/g/0/d/f', str(active_fret)) #TODO use config for id

def strum(velocity):
    global strumming
    print("STRUM")
    strumming = True
    client.publish('i/g/0/d/s', str(velocity)) #TODO use config for id


def sample(verbose=False):
    global strumming
    max_diff  = 0
    best_fret = 0
    for i, t in enumerate(fret_sensors):
        cap_val = touch_thresh - t.read()
        if verbose:
            print(i, cap_val)
        if cap_val >  max_diff:
            max_diff = cap_val
            best_fret = i + 1
    if best_fret != active_fret:
        update_fret(best_fret)
    strum_val = touch_thresh - strum_sensor.read()
    if verbose:
        print("Strum:", strum_val)
    if strum_val > 0 and strumming is False:
        strum(strum_val)
    elif strumming is True and strum_val <= 0:
        strumming = False
