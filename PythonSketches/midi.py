import time
import rtmidi
import sys

# TODO add flats as well
base_notes = {
    'c'     : 0,
    "c#"    : 1,
    "d"     : 2,
    "d#"    : 3,
    "e"     : 4,
    "f"     : 5,
    "f#"    : 6,
    "g"     : 7,
    "g#"    : 8,
    "a"     : 9,
    "a#"    : 10,
    "b"     : 11
}

note_list_sharps = ['C', "C#", 'D', "D#", 'E', 'F', "F#", 'G', "G#", 'A', "A#", 'B']
note_list_flats = ['C', "Db", 'D', "Eb", 'E', 'F', "Gb", 'G', "Ab", 'A', "Bb", 'B']
note_list = [s if s == f else s + '/' + f for s,f in zip(note_list_sharps, note_list_flats)]

# Convert note names to corresponding MIDI decimal
# i.e. 'C4' ->  60 or 'D#' -> 63
# note_name: str that may or may not include octave
# octave: optionally specify octave (-1 to 7) with int
def note_to_MIDI(note_name, octave=None):
    if octave is None:
        if note_name[-1].isdigit():
            octave = int(note_name[-1])
        else:
            octave = 4
    return base_notes[note_name.lower()] + 12 * (octave+1)

# Inverse of above. Since note-MIDI mapping is not one-to-one,
# you can specify whether you want the black keys as flats or sharps.
# Default behavior includes both flat and sharp name
def MIDI_to_note(midi_id, sharps_only=False, flats_only=False):
    octave = (midi_id // 12) - 1
    note_i = midi_id % 12
    if sharps_only:
        return note_list_sharps[note_i] + str(octave)
    if flats_only:
        return note_list_flats[note_i] + str(octave)
    else:
        return note_list[note_i] + str(octave)



class Instrument:

    def __init__(self):
        self.signal_cutoff = 350
        self.playing = False
        self.midiout = rtmidi.MidiOut()
        self.duration = .25
        available_ports = self.midiout.get_ports()
        if available_ports:
            self.midiout.open_port(0)
            print("Selected first available port")
        else:
            self.midiout.open_virtual_port("My virtual output")
            print("Opened virtual port")

    def note_num(self, note):
        return self.notes[note]

    def play_note(self, n):
        if n in self.notes:
            self.note = self.notes[n]
            print("Playing",n)
            note_on = [0x90, self.notes[n], 112] # channel 1, middle C, velocity 112
            note_off = [0x80, self.notes[n], 0]
            self.midiout.send_message(note_on)
            time.sleep(self.duration)
            self.midiout.send_message(note_off)

    def start_c(self, velocity=112):
        print("Note ON")
        self.playing = True
        self.midiout.send_message([0x90, 60+self.note, velocity])

    def stop_c(self):
        print("Note OFF")
        self.playing = False
        self.midiout.send_message([0x90, 60+self.note, 0])

    def stop_all(self):
        print("Halting instrument sounds")
        self.midiout


    # del midiout
