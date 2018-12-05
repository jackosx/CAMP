# Python Sketches

## Dependencies

 * rtMidiPython
 * OpenCV
 * Paho MQTT Client
 * Mosquitto MQTT Broker

## Other Tools
* Ableton or other DAW that supports multiple MIDI inputs
* MQTTBox
  * For debugging, doesn't necessarily have to be this one. Can also use `mosquitto_pub` and `mosquitto_sub`
  CL-tools included with Mosquitto

## Langenizer
The core modules that open MIDI ports, communicate with ESP32 hardware via MQTT, and orchestrate performance.

## rtmidiex.py
A simple example that demonstrates how a Python program can be used to generate high-quality sounding music.
The program produces a stream of MIDI messages that are synthesized by GarageBand. It is shockingly easy to confiugre.
Just open GarageBand, add an instrument to the track, and the virtual port opened by rtMIDI will automatically
connect when the program runs.

Run via `$ python rtmidiex.py [sequence of notes] [note duration]`

## thresh.py
Turn a brightly colored rod into a silly MIDI instrument. Based on an OpenCV thresholding example, run the program and
adjust the threshold sliders to isolate the rod. Grab the rod somewhere to divide the bounding box into two. The ratio of
the bounding boxes determines the note that the `instrument` will play. The notes are played at a regular interval, only
the pitch changes depending on hand position.

## mqmidi.py
Demonstrates that an ESP32 with capacitive sensor can relay data to a host machine to act as a wireless instrument. This
demo requires an ESP32 unit that has been set up on the same network as the host machine and MQTT broker. The ESP32
should publish raw capacitive sensor output to the topic `sensors/+`. The `+` is the index of the sensor; it can be anything
in the current sketch, eventually will be used to distinguish fretboard positions.
