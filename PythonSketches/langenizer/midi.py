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
import threading
import queue
import genres

# TODO Note class? With MIDI and note name?
base_notes = {
    'c': 0,
    "c#": 1,
    "db": 1,
    "c#/db": 1,
    "d": 2,
    "d#": 3,
    "eb": 3,
    "d#/eb": 3,
    "e": 4,
    "f": 5,
    "f#": 6,
    "gb": 6,
    "f#/gb": 7,
    "g": 7,
    "g#": 8,
    "ab": 9,
    "g#/ab": 9,
    "a": 9,
    "a#": 10,
    "bb": 10,
    "a#/b#": 10,
    "b": 11
}

note_list_sharps = ['C', "C#", 'D', "D#",
                    'E', 'F', "F#", 'G', "G#", 'A', "A#", 'B']
note_list_flats = ['C', "Db", 'D', "Eb", 'E',
                   'F', "Gb", 'G', "Ab", 'A', "Bb", 'B']
note_list = [s if s == f else s + '/' + f for s,
             f in zip(note_list_sharps, note_list_flats)]

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
        raise ValueError(
            "Invalid MIDI note. Expecting integer in range 0-127. Got", midi_id)
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

    def __init__(self, midi_channel=0, midi_name="Python"):
        self.midi_channel = midi_channel
        self.midiout = rtmidi.MidiOut()
        self.duration = .25
        self.notes_on = Counter()  # need to count how many times we turn on each note
        available_ports = self.midiout.get_ports()
        if available_ports:
            self.midiout.open_port(0)
            print("Selected first available port")
        else:
            self.midiout.open_virtual_port(midi_name)
            print("Opened", midi_name, "virtual port")

        self.midi_queue = queue.PriorityQueue()
        self.halt_flag = -1 # -1 is off, o.w. use number of queued notes to cancel on halt
        self.worker = threading.Thread(target=self.async_work)
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.worker.start()

    def async_work(self):
        has_item_or_halt = lambda : not self.midi_queue.empty() or self.halt_flag != -1
        def halt_all():
            # Empty remaining
            for i in range(self.halt_flag):
                if not self.midi_queue.empty():
                    self.midi_queue.get_nowait()
                    print("EMPTIED")
            for n_id, count in self.notes_on.items():
                for i in range(count):
                    self.midiout.send_message([0x80 + self.midi_channel, n_id, 0])
                self.notes_on[n_id] = 0
            self.halt_flag = -1
        # Work Loop
        while True:
            with self.cv:
                self.cv.wait_for(has_item_or_halt)
                if self.halt_flag != -1:
                    halt_all()
                else:
                    midi_msg, delay = self.midi_queue.get_nowait()
                    channel, midi_id, velocity = midi_msg
                    if delay is not None:
                        time.sleep(delay)
                    if velocity > 0:
                        self.notes_on[midi_id] += 1
                    else:
                        self.notes_on[midi_id] -= 1
                    self.midiout.send_message(midi_msg)



    def send_midi_async(self, midi_msg, delay=None):
        with self.cv:
            self.midi_queue.put((midi_msg, delay))
            self.cv.notifyAll()

    # Send Note-On MIDI Message
    def play_note(self, note_name=None, velocity=100, midi_id=None, delay=None):
        if note_name is not None and midi_id is None:
            midi_id = note_to_MIDI(note_name)
        elif midi_id is not None and note_name is None:
            note_name = MIDI_to_note(midi_id)
        elif note_name is None and midi_id is None:
            raise ValueError("No note to play provided!")
        elif note_to_MIDI(note_name) != midi_id:
            raise ValueError("Provided note {} does not match provided MIDI id {}".format(
                note_name, midi_id))
        note_on = [0x90+self.midi_channel, midi_id, velocity]
        self.send_midi_async(note_on,delay)
        # # print("Playing", note_name)  # TODO make for verbose mode only
        # if duration is not None:
        #     time.sleep(duration)
        #     self.stop_note(midi_id=midi_id)


    # Send Note-Off MIDI Message
    def stop_note(self, note_name=None, midi_id=None):
        if note_name is not None and midi_id is None:
            midi_id = note_to_MIDI(note_name)
        elif midi_id is not None and note_name is None:
            note_name = MIDI_to_note(midi_id)
        elif note_name is None and midi_id is None:
            raise ValueError("No note provided!")
        elif note_to_MIDI(note_name) != midi_id:
            raise ValueError("Provided note {} does not match provided MIDI id {}".format(
                note_name, midi_id))
        # channel 1, middle C, velocity 112
        note_off = [0x80+self.midi_channel, midi_id, 0]
        self.send_midi_async(note_off)
        # print("Stopped", note_name)  # TODO make for verbose mode only

    # Send Note-Off MIDI Message for all playing notes
    def stop_all(self):
        # print("Halting instrument sounds")
        with self.cv:
            self.halt_flag = self.midi_queue.qsize()
            self.cv.notifyAll()

        # Neither of these were stopping the notes in Garageband
        # self.midiout.send_message([self.midi_channel, 120])
        # self.midiout.send_message([0xB0+self.midi_channel, 123, 0])
    # del midiout

    def set_genre(self, genre):
        print("Not implemented for pure Python instrument")

    # Set midi channel
    def set_midi_channel(self, channel):
        self.midi_channel = channel


class Guitar(Instrument):
    def __init__(self, channel=0x0, key="C", octave=3, midi_name="Guitar"):
        self.active_fret = 0
        self.set_key(key, octave)
        Instrument.__init__(self, channel, midi_name=midi_name)

    def set_key(self, key, octave):
        self.key = key
        self.octave = octave
        self.chords = [Chords.get_five(key, octave=octave-1, use_names=True),
                       Chords.get_one(key, octave, True),
                       Chords.get_four(key, octave, True),
                       Chords.get_five(key, octave, True),
                       Chords.get_one(key, octave+1, True),
                       Chords.get_four(key, octave+1, True),
                       Chords.get_five(key, octave+1, True),
                       Chords.get_one(key, octave+2, True)]

    def set_fret(self, fret_num):
        # if self.active_fret == fret_num:
        #     return
        self.stop_all()  # STOP Playing on fret change
        self.active_fret = fret_num

    # Need strum worker thread
    def strum(self, velocity=100):
        for i, note in enumerate(self.chords[self.active_fret]):
            delay = 0.025
            self.play_note(note_name=note, velocity=velocity, delay=delay)

    def set_genre(self, genre):
        self.midi_channel = genre.channel


class Bass(Guitar):
    def __init__(self, channel=0x1, key="C", octave=2, midi_name="Bass"):
        Guitar.__init__(self, channel, key, octave, midi_name)
        self.set_key(key, octave)

    def set_key(self, key, octave):
        self.key = key
        self.octave = octave
        # e e g e d c b
        # 6 6 8 6 5 4 3
        # 9 9 0 9 7 5 4
        root = note_to_MIDI(note_name=key, octave=octave)
        #             | 0  |   1   |   2   |   3   |   4   |   5   |
        intervals = [0, 4, 5, 7, 9, 12, 13]
        self.chords = [(MIDI_to_note(root + i),) for i in intervals]

    def set_genre(self, genre):
        print("Changing bass channel from", self.midi_channel, "to", genre.channel)
        self.midi_channel = genre.channel

# ASSUMPTION: 4/4 time
# Things to measure: speed, velocity, count, trends among these vars?
# Bifurcate based on low-v-high velocity strikes?
# Use flags or callbacks?
class LiveMeter:
    reset_threshold = .25

    # Motivation for seemingly arbitrary thresholds:
    # Other method would be to see if implied_BPM
    # is closer to 1*BPM or 2*BPM, 2*BPM or 4*BPM
    # and bucket linearly based on that
    # This may allow us to tune better-feeling,
    # non-linear buckets (maybe)
    half_threshold = .6
    eighth_threshold = 1.9
    sixteenth_threshold = 3.5

    # Double check gets/sets are efficient and correct
    @property
    def sixteenth_count(self):
        return self._sixteenth_count
    @sixteenth_count.setter
    def sixteenth_count(self, value):
        self._sixteenth_count = value % 16

    @property
    def eighth_count(self):
        return self._sixteenth_count // 2
    @eighth_count.setter
    def eighth_count(self, value):
        self._eighth_count = value % 8
        self._sixteenth_count = self._eighth_count * 2

    @property
    def beat_count(self):
        return self._sixteenth_count // 4
    @beat_count.setter
    def beat_count(self, value):
        self._beat_count = value % 4
        self._eighth_count = self._beat_count * 2
        self._sixteenth_count = self._beat_count * 4


    def __init__(self, bpm=110):
        self.set_bpm(bpm)
        self.last_timestamp = 0
        self.was_beat      = False
        self.was_eighth    = False
        self.was_sixteenth = False
        self.beat_count = 0

    def set_bpm(self, bpm):
        self.bpm = bpm

    def record_input(self, velocity=90):
        new_time = time.clock_gettime(0)
        diff = new_time - self.last_timestamp # Need to figure out diff b/w sticks?
        implied_BPM = 60/diff
        self.last_timestamp = new_time
        print("Implied BPM:{:.0f}".format(implied_BPM))
        if implied_BPM > LiveMeter.sixteenth_threshold * self.bpm:
            self.was_sixteenth = True
            self.sixteenth_count += 1
                # Two quick ones...but not sure what it means?
            print("16th")
        elif implied_BPM > LiveMeter.eighth_threshold * self.bpm:
            # Do eighth note things (half beat)
            self.eighth_count += 1
            self.was_sixteenth = False # Rule: Cannot be faster than test?
            self.was_eighth = True
            self.was_beat = not self.was_beat
        elif implied_BPM < LiveMeter.reset_threshold * self.bpm:
            # PERFORM RESET
            self.sixteenth_count = 0
            self.was_beat = True
            self.was_eighth = False
            self.was_sixteenth = False
        else: #presumably slow, beat setting? not accounting for half notes yet
            self.was_beat = True
            self.was_eighth = False
            self.was_sixteenth = False
            self.beat_count += 1


# Per Drumstick:
# Should these vars be single notes, or possible tuples?
# Half_notes: [a, b]
# Quarter_notes: [a, b, c, d]
# Eighth_notes: [a, b, c, d,
#                e, f, g, h]
# Sixteenth_notes: [a, b, c, d,
#                   e, f, g, h,
#                   i, j, k, l
#                   m, n, o, p]
# Boolean was_thing flags enable this tiered setting, otherwise simple
# array of 16 notes
# Tiered system basically enables 'intensity'
# Alternatively, have different 16-note sequences for different intensities
# For example, imagine someone drumming twice in a measure — probably want "dum"-"dum"
# But if going faster may want snare or cymbal with kick on downbeat? Or would this be covered by the second stick?
class Drum(Instrument):
    def __init__(self, channel=9, midi_name="Drums",drum_id=0):
        Instrument.__init__(self, channel, midi_name=midi_name)
        self.drum_id = drum_id
        self.strike_timestamp = 0
        self.lm = LiveMeter()
        self.set_genre(genres.genre_list[0]) # TODO: improve

    def play_hit(self, note_name=None, velocity=90):
        self.play_note(note_name=note_name, velocity=velocity)
        self.stop_note(note_name=note_name)

    # Probably remove drum_num arg since one instance per stick?
    def strike(self, velocity=90):
        self.lm.record_input(velocity)
        self.play_hit(self.quarters[self.lm.beat_count],velocity=velocity)
        # if self.lm.was_beat:
        #     self.play_hit(self.quarters[self.lm.beat_count],velocity=velocity)
        # if self.lm.was_eighth: # Only true on beat if the previous hit was half a beat away
        #     self.play_hit(self.eighths[self.lm.eighth_count],velocity=velocity)
        #     print("EIGHTH")
        # if self.lm.was_sixteenth:
        #     print("Sixteenth")
        #     self.play_hit(self.sixteenths[self.lm.sixteenth_count],velocity=velocity)

    def set_genre(self, genre):
        drums = genre.drums[self.drum_id]
        self.halves = drums.halves
        self.quarters = drums.quarters
        self.eighths = drums.eighths
        self.sixteenths = drums.sixteenths
