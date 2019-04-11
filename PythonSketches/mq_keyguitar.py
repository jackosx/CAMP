from pynput import keyboard
from langenizer import midi
import paho.mqtt.client as mqtt

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # client.subscribe("sensors/+")client = mqtt.Client()

client.on_connect = on_connect
# client.on_message = on_message

client.connect("manatee.local", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

guitar_topic = '/i/g/0/d/'
# guitar = midi.Guitar()
keys_pressed = set()
valid_keys = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}

def on_press(key):
    try:
        if key not in keys_pressed:
            keys_pressed.add(key)
            if key == keyboard.Key.space:
                print("strumming")
                client.publish(guitar_topic + 's', 100)
                return
            k = key.char
            # if k.isalpha() and k in valid_keys:
                # guitar.play_note(k)
            if k.isdigit() and int(k) < 5:
                client.publish(guitar_topic + 'f', k)
            if k == 's':
                client.publish(guitar_topic + 's', 100)

        # print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))
    except ValueError:
        print('error playing note')

def on_release(key):
    # print('{0} released'.format(key))
    keys_pressed.remove(key)
    if key == keyboard.Key.esc:
        # Stop listener
        return False
    if key == keyboard.Key.space:
        return
    try:
        k = key.char
        if k.isdigit():
            client.publish(guitar_topic + 'f', 0)
    except AttributeError:
        print('special key {0} pressed'.format(key))


# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
