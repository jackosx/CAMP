"""
Handles MIDI operations such as transforming human-readable
music notes to MIDI data, then piping it to virtual MIDI ports
to be played by a DAW such as GarageBand (not a full DAW with
support for multiple simultaneous MIDI inputs) or Ableton Live
(a much better choice, but not free)

Contains Instrument base class, which is extended to
Drum, Guitar, and Bass classes (Bass extends guitar)
"""

import time
import rtmidi
import sys
from collections import Counter

# TODO Note class? With MIDI and note name?
base_notes = {
    'c'     : 0,
    "c#"    : 1,
    "db"    : 1,
    "c#/db" : 1,
    "d"     : 2,
    "d#"    : 3,
    "eb"    : 3,
    "d#/eb" : 3,
    "e"     : 4,
    "f"     : 5,
    "f#"    : 6,
    "gb"    : 6,
    "f#/gb" : 7,
    "g"     : 7,
    "g#"    : 8,
    "ab"    : 9,
    "g#/ab" : 9,
    "a"     : 9,
    "a#"    : 10,
    "bb"    : 10,
    "a#/b#" : 10,
    "b"     : 11
}

note_list_sharps = ['C', "C#", 'D', "D#", 'E', 'F', "F#", 'G', "G#", 'A', "A#", 'B']
note_list_flats = ['C', "Db", 'D', "Eb", 'E', 'F', "Gb", 'G', "Ab", 'A', "Bb", 'B']
note_list = [s if s == f else s + '/' + f for s,f in zip(note_list_sharps, note_list_flats)]

# TODO handle note mapping failures

# Convert note names to corresponding MIDI decimal
# i.e. 'C4' ->  60 or 'D#' -> 63
# note_name: str that may or may not include octave
# octave: optionally specify octave (-1 to 7) with int
def note_to_MIDI(note_name, octave=None):
    if note_name is None:
        raise ValueError("No note provided!")
    if octave is None:
        if note_name[-1].isdigit():
            octave = int(note_name[-1])
            note_name = note_name[:-1]
        else:
            octave = 4
    try:
        return base_notes[note_name.lower()] + 12 * (octave+1)
    except (KeyError):
        raise ValueError("Invalid note provided", note_name)


# Inverse of above. Since note-MIDI mapping is not one-to-one,
# you can specify whether you want the black keys as flats or sharps.
# Default behavior includes both flat and sharp name
def MIDI_to_note(midi_id, sharps_only=False, flats_only=False):
    if midi_id > 127 or midi_id < 0:
        raise ValueError("Invalid MIDI note. Expecting integer in range 0-127. Got", midi_id)
    octave = (midi_id // 12) - 1
    note_i = midi_id % 12
    if sharps_only:
        return note_list_sharps[note_i] + str(octave)
    if flats_only:
        return note_list_flats[note_i] + str(octave)
    else:
        return note_list[note_i] + str(octave)

# TODO make these more parameterized
class Chords:

    def get_one(root, octave=None, use_names=False):
        root_id = root
        if use_names:
            root_id = note_to_MIDI(root, octave=octave)
        note_ids = (root_id, root_id + 4, root_id + 7)
        if use_names:
            return (root, MIDI_to_note(note_ids[1]), MIDI_to_note(note_ids[2]))
        else:
            return note_ids

    def get_four(root, octave=None, use_names=False):
        root_id = root
        if use_names:
            root_id = note_to_MIDI(root, octave=octave)
        fourth = root_id + 5
        note_ids = Chords.get_one(fourth)
        if use_names:
            return tuple(MIDI_to_note(n) for n in note_ids)
        else:
            return note_ids

    def get_five(root, octave=None, use_names=False):
        root_id = root
        if use_names:
            root_id = note_to_MIDI(root, octave=octave)
        fifth = root_id + 7
        note_ids = Chords.get_one(fifth)
        if use_names:
            return tuple(MIDI_to_note(n) for n in note_ids)
        else:
            return note_ids



class Instrument:

    def __init__(self, midi_channel=0):
        self.midi_channel = midi_channel
        self.midiout = rtmidi.MidiOut()
        self.duration = .25
        self.notes_on = Counter() # need to count how many times we turn on each note
        available_ports = self.midiout.get_ports()
        if available_ports:
            self.midiout.open_port(0)
            print("Selected first available port")
        else:
            self.midiout.open_virtual_port("My virtual output")
            print("Opened virtual port")

    # Send Note-On MIDI Message
    def play_note(self, note_name=None, velocity=100, midi_id=None, duration=None):
        if note_name is not None and midi_id is None:
            midi_id = note_to_MIDI(note_name)
        elif midi_id is not None and note_name is None:
            note_name = MIDI_to_note(midi_id)
        elif note_name is None and midi_id is None:
            raise ValueError("No note to play provided!")
        elif note_to_MIDI(note_name) != midi_id:
            raise ValueError("Provided note {} does not match provided MIDI id {}".format(note_name, midi_id))

        note_on = [0x90+self.midi_channel, midi_id, velocity] # channel 1, middle C, velocity 112
        self.midiout.send_message(note_on)
        self.notes_on[midi_id] += 1
        print("Playing",note_name) # TODO make for verbose mode only

        if duration is not None:
            time.sleep(duration)
            self.stop_note(midi_id=midi_id)

    # Send Note-Off MIDI Message
    def stop_note(self, note_name=None, midi_id=None):
        if note_name is not None and midi_id is None:
            midi_id = note_to_MIDI(note_name)
        elif midi_id is not None and note_name is None:
            note_name = MIDI_to_note(midi_id)
        elif note_name is None and midi_id is None:
            raise ValueError("No note provided!")
        elif note_to_MIDI(note_name) != midi_id:
            raise ValueError("Provided note {} does not match provided MIDI id {}".format(note_name, midi_id))

        # TODO: Check if note is playing before sending?
        note_off = [0x80+self.midi_channel, midi_id, 0] # channel 1, middle C, velocity 112
        self.midiout.send_message(note_off)
        self.notes_on[midi_id] -= 1
        print("Stopped", note_name) # TODO make for verbose mode only

    # Send Note-Off MIDI Message for all playing notes
    def stop_all(self):
        print("Halting instrument sounds")
        for n_id, count in self.notes_on.items():
            for i in range(count):
                self.midiout.send_message([0x80 + self.midi_channel, n_id, 0])
            self.notes_on[n_id] = 0
        # Neither of these were stopping the notes in Garageband
        # self.midiout.send_message([self.midi_channel, 120])
        # self.midiout.send_message([0xB0+self.midi_channel, 123, 0])



    # del midiout

class Guitar(Instrument):
    def __init__(self, channel=0x0, key="C", octave=3):
        self.active_fret = 0
        self.set_key(key, octave)
        Instrument.__init__(self, channel)

    def set_key(self, key, octave):
        self.key    = key
        self.octave = octave
        self.chords = [Chords.get_five(key, octave=octave-1, use_names=True),
                       Chords.get_one(key, octave, True),
                       Chords.get_four(key, octave, True),
                       Chords.get_five(key, octave, True),
                       Chords.get_one(key, octave+1, True),
                       Chords.get_four(key, octave+1, True),
                       Chords.get_five(key, octave+1, True)]

    def set_fret(self, fret_num):
        # if self.active_fret == fret_num:
        #     return
        self.stop_all() # STOP Playing on fret change
        self.active_fret = fret_num

    # Need strum worker thread
    def strum(self, velocity=100):
        for note in self.chords[self.active_fret]:
            self.play_note(note_name=note, velocity=velocity)


class Bass(Guitar):
    def __init__(self, channel=0x1, key="C", octave=2):
        Guitar.__init__(self, channel, key, octave)
        self.set_key(key, octave)

    def set_key(self, key, octave):
        self.key    = key
        self.octave = octave
        # e e g e d c b
        # 6 6 8 6 5 4 3
        # 9 9 0 9 7 5 4
        root = note_to_MIDI(note_name=key, octave=octave)
        #             | 0  |   1   |   2   |   3   |   4   |   5   |
        intervals = [0, 4, 5, 7, 9, 12]
        self.chords = [(MIDI_to_note(root + i),) for i in intervals]


class Drum(Instrument):
    def __init__(self, channel=9):
        Instrument.__init__(self, channel)
        self.drums = ['f2', 'd2', 'a#2']

    def strike(self, drum_num, velocity):
        self.play_note(note_name=self.drums[drum_num], velocity=velocity)
        self.stop_note(note_name=self.drums[drum_num])
