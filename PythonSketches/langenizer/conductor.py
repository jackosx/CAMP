"""
Takes messages from ESP32 instruments and generates MIDI. Can use
metronome class to quantize playing rhythm.

"""

import paho.mqtt.client as mqtt
import midi
import metronome

m = metronome.ticker.start()

guitars = [midi.Guitar(key="G", octave=3), midi.Bass(key='G',octave=1)]
drums = midi.Drum()

def on_guitar_message(client, userdata, msg):
    print("Guitar Message", msg.topic, msg.payload)
    guitar_num = int(msg.topic[4])
    guitar     = guitars[guitar_num]
    action     = msg.topic[6]
    sensor_val = int(msg.payload)
    if action == 'd':
        user_action = msg.topic[8]
        print(user_action)
        if user_action == 's':
            print("Strum")
            guitar.strum(sensor_val)
            # metronome.on_next_beat(guitar.strum, sensor_val)
        elif user_action == 'f':
            guitar.set_fret(sensor_val)

def on_drum_message(client, userdata, msg):
    # i/ d/id/ d/ s/ n
    # 0| 2| 4| 6| 8|10
    drumkit_num = int(msg.topic[4])
    sensor_val = int(msg.payload)
    action     = msg.topic[6]
    print("Drum Message", msg.topic, sensor_val)
    if action == 'd': # d for 'data'
        user_action = msg.topic[8]
        print(user_action)
        if user_action == 's': # s for strum
            print("Drum")
            drum_num = int(msg.topic[10])
            drums.strike(drum_num, sensor_val)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # Topic format
    # i/{g,d}/{inst_num}/{d,c}/[xtra]
    client.subscribe("i/+/+/#")
    client.message_callback_add("i/g/+/#", on_guitar_message) # for guitar messages
    client.message_callback_add("i/d/+/#", on_drum_message)



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Unhandled message:" + msg.topic+" "+str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("manatee.local", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
