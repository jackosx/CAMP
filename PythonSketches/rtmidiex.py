import time
import rtmidi
import sys

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

notes_in = ""
if len(sys.argv) < 2:
    notes_in = input("Type some notes:")
else:
    notes_in = sys.argv[1]
print(notes_in)
for n in notes_in:
    play_note(n)

del midiout
