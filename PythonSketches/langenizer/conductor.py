"""
Takes messages from ESP32 instruments and generates MIDI. Can use
metronome class to quantize playing rhythm.

"""

import paho.mqtt.client as mqtt
from pythonosc import dispatcher
from pythonosc import osc_server
import midi
import metronome

m = metronome.ticker.start()

guitars = [midi.Guitar(key="G", octave=3), midi.Bass(key='G',octave=1)]
drums = midi.Drum()

def on_guitar_message_mqtt(client, userdata, msg):
    on_guitar_message(msg.topic, msg.payload)

def on_guitar_message(channel, payload):
    print("Guitar Message", channel, payload)
    guitar_num = int(channel[5])
    guitar     = guitars[guitar_num]
    action     = channel[7]
    sensor_val = int(float(payload))
    if action == 'd':
        user_action = channel[9]
        print(user_action)
        if user_action == 's':
            print("Strum")
            guitar.strum(sensor_val)
            # metronome.on_next_beat(guitar.strum, sensor_val)
        elif user_action == 'f':
            guitar.set_fret(sensor_val)

def on_drum_message_mqtt(client, userdata, msg):
    on_drum_message(msg.topic, msg.payload)

def on_drum_message(channel, payload):
    drumkit_num = int(channel[5])
    sensor_val = int(float(payload))
    action     = channel[7]
    print("Drum Message", channel, sensor_val)
    if action == 'd': # d for 'data'
        user_action = channel[9]
        print(user_action)
        if user_action == 's': # s for strum
            print("Drum")
            drum_num = int(channel[11])
            drums.strike(drum_num, sensor_val)


# The callback for when the client receives a CONNACK response from the server.
def on_connect_mqtt(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # Topic format
    # i/{g,d}/{inst_num}/{d,c}/[xtra]
    client.subscribe("i/+/+/#")
    client.message_callback_add("i/g/+/#", on_guitar_message_mqtt) # for guitar messages
    client.message_callback_add("i/d/+/#", on_drum_message_mqtt)



# The callback for when a PUBLISH message is received from the server.
def on_message_mqtt(client, userdata, msg):
    print("Unhandled message:" + msg.topic+" "+str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect_mqtt
client.on_message = on_message_mqtt

client.connect("manatee.local", 1883, 60)

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/*", print)
dispatcher.map("/i/g/*", on_guitar_message)
dispatcher.map("/i/d/*", on_drum_message)
server = osc_server.ThreadingOSCUDPServer(
  ("jack.local", 5005), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
