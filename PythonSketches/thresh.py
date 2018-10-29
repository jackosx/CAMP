import cv2 as cv
import argparse
import numpy as np
"""
Old PyAudio Code
import pyaudio

p = pyaudio.PyAudio()

volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 0.1   # in seconds, may be float
f = 440.0        # sine frequency, Hz, may be float
sounds = [ (np.sin(i*.25*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32) for i in range(10)]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)"""

import time
import rtmidi
import sys

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

cur_note = -1
midi_delay = 5
midi_counter = 0

def stop_note():
    if cur_note >= 0:
        print("Stopping",cur_note)
        note_off = [0x80, cur_note, 0]
        midiout.send_message(note_off)

def play_note(n):
    stop_note()
    global cur_note
    print(cur_note)
    cur_note = n
    print("Starting",n)
    note_on = [0x90, int(n), 112] # channel 1, middle C, velocity 112
    midiout.send_message(note_on)



max_value = 255
max_value_H = 360//2
low_H = 112
low_S = 100
low_V = 0
high_H = 125
high_S = max_value
high_V = max_value
window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'
low_H_name = 'Low H'
low_S_name = 'Low S'
low_V_name = 'Low V'
high_H_name = 'High H'
high_S_name = 'High S'
high_V_name = 'High V'

max_area = 4000;

def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = val
    low_H = min(high_H-1, low_H)
    cv.setTrackbarPos(low_H_name, window_detection_name, low_H)
def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = val
    high_H = max(high_H, low_H+1)
    cv.setTrackbarPos(high_H_name, window_detection_name, high_H)
def on_low_S_thresh_trackbar(val):
    global low_S
    global high_S
    low_S = val
    low_S = min(high_S-1, low_S)
    cv.setTrackbarPos(low_S_name, window_detection_name, low_S)
def on_high_S_thresh_trackbar(val):
    global low_S
    global high_S
    high_S = val
    high_S = max(high_S, low_S+1)
    cv.setTrackbarPos(high_S_name, window_detection_name, high_S)
def on_low_V_thresh_trackbar(val):
    global low_V
    global high_V
    low_V = val
    low_V = min(high_V-1, low_V)
    cv.setTrackbarPos(low_V_name, window_detection_name, low_V)
def on_high_V_thresh_trackbar(val):
    global low_V
    global high_V
    high_V = val
    high_V = max(high_V, low_V+1)
    cv.setTrackbarPos(high_V_name, window_detection_name, high_V)
parser = argparse.ArgumentParser(description='Code for Thresholding Operations using inRange tutorial.')
parser.add_argument('--camera', help='Camera devide number.', default=0, type=int)
args = parser.parse_args()
cap = cv.VideoCapture(args.camera)
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)
cv.createTrackbar(low_H_name, window_detection_name , low_H, max_value_H, on_low_H_thresh_trackbar)
cv.createTrackbar(high_H_name, window_detection_name , high_H, max_value_H, on_high_H_thresh_trackbar)
cv.createTrackbar(low_S_name, window_detection_name , low_S, max_value, on_low_S_thresh_trackbar)
cv.createTrackbar(high_S_name, window_detection_name , high_S, max_value, on_high_S_thresh_trackbar)
cv.createTrackbar(low_V_name, window_detection_name , low_V, max_value, on_low_V_thresh_trackbar)
cv.createTrackbar(high_V_name, window_detection_name , high_V, max_value, on_high_V_thresh_trackbar)
while True:

    ret, frame = cap.read()
    if frame is None:
        break
    frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV) # use cv.bitwise_not( for red
    frame_threshold = cv.inRange(frame_HSV, (low_H, low_S, low_V), (high_H, high_S, high_V))

    contours =  cv.findContours(frame_threshold,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)[-2]
    s_contours = sorted(contours, key=lambda c: cv.contourArea(c))[-2:]
    print(s_contours)
    if len(s_contours) >= 1 and cv.contourArea(s_contours[-1]) > 1000:
        for c in s_contours[-2:]:
            epsilon = 0.1*cv.arcLength(c,True)
            prox = cv.approxPolyDP(c,epsilon,True)
            cv.drawContours(frame, [prox], -1, (0,255,0), 3)
            rect = cv.minAreaRect(c)
            box = cv.boxPoints(rect)
            box = np.int0(box)
            im = cv.drawContours(frame,[box],0,(0,0,255),2)
        if midi_counter >= midi_delay:
            ratio = cv.contourArea(s_contours[-2]) / cv.contourArea(s_contours[-1])
            i = 50 + int(10*ratio)
            play_note(i)
            midi_counter = 0
        midi_counter = midi_counter + 1

    cv.imshow(window_capture_name, frame)
    cv.imshow(window_detection_name, frame_threshold)

    key = cv.waitKey(30)
    if key == ord('q') or key == 27:
        stop_note()
        break
