
import machine
from umqtt.simple import MQTTClient
import config

drumpad_id = config.id

client = MQTTClient("drumpad-{}".format(config.id), "manatee.local")
client.connect()

# See wiki for pinout: https://github.com/jackosx/CAMP/wiki/ESP32-Hardware

pad_sensors = [machine.TouchPad(machine.Pin(p)) for p in config.pad_pins]
pads_touched = [False for p in pad_sensors]

touch_thresh = config.threshold

def set_touch_thresh(new_thresh):
    global touch_thresh
    touch_thresh = new_thresh

def strike(new_pad, velocity):
    print("STRIKE",  new_pad, velocity)
    pads_touched[new_pad] = True
    client.publish('i/d/{}/d/s/{}'.format(drumpad_id, new_pad), str(new_pad)) 
def sample(verbose=False):
    for i, t in enumerate(pad_sensors):
        cap_diff = touch_thresh - t.read()
        if verbose:
            print(i, cap_diff)
        is_touched = pads_touched[i]
        if cap_diff >  0 and not is_touched:
            strike(i, cap_diff)
        elif cap_diff <= 0 and is_touched:
            pads_touched[i] = False
