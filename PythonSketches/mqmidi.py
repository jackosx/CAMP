import time
import rtmidi
import sys

signal_cutoff = 500
playing = False

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

time.sleep(.5)
duration = .25
if len(sys.argv) > 2:
    duration = float(sys.argv[2])

notes = {
            'a' : 57,
            'b' : 59,
            'c' : 60,
            'd' : 62,
            'e' : 64,
            'f' : 65,
            'g' : 67
         }

def play_note(n):
    if n in notes:
        print("Playing",n)
        note_on = [0x90, notes[n], 112] # channel 1, middle C, velocity 112
        note_off = [0x80, notes[n], 0]
        midiout.send_message(note_on)
        time.sleep(duration)
        midiout.send_message(note_off)

def start_c(velocity=112):
    print("Note ON")
    global playing
    playing = True
    midiout.send_message([0x90, 60, velocity])

def stop_c():
    print("Note OFF")
    global playing
    playing = False
    midiout.send_message([0x90, 60, 0])


import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe("sensors/+")


# The callback for when a PUBLISH message is received from the server.
counter = 0
count_max = 50
def on_message(client, userdata, msg):
    global counter
    # print(msg.topic+" "+str(msg.payload))
    # print("Playing:",playing)
    signal_mag = int(msg.payload)
    print(signal_mag)
    if signal_mag > signal_cutoff and playing is True:
        stop_c()

    if playing is True:
    #     counter = counter + 1
    #     if counter > count_max:
    #         counter = 0
            start_c((signal_cutoff - signal_mag) * 127 / signal_cutoff)

    if signal_mag < signal_cutoff and playing is False:
        start_c(min(signal_cutoff - signal_mag, 127))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.1.16", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()


del midiout
