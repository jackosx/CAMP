import langenizer.timers as timers
import mock_esps
import time

#==============================================================================
# MOCK INSTRUMENTS
guitar = mock_esps.Guitar(id=0)
bass = mock_esps.Guitar(id=1)
drum = mock_esps.Drumstick()
#==============================================================================
# Initialize Counters
ticks = 0
frequency = 32 # 32 ticks per beat
meter = 4
# Use these each tick to determine if we're in the same "beat" window
prev_4 = -1
prev_8 = -1
prev_16 = -1

strike_timestamp = 0

def hit_beat():
    global strike_timestamp
    bass.strum_fret(count_beat())
    print("BEAT", count_beat())
    drum.strike()
    guitar.strum_fret(count_beat())

    new_time = time.clock_gettime(0)
    diff = new_time - strike_timestamp # Need to figure out diff b/w sticks?
    implied_BPM = 60/diff
    strike_timestamp = new_time
    # print("Time from last beat:", diff)
    print("Implied BPM:{:.0f}".format(implied_BPM))

def hit_eighth():
    if count_8() == 1 and (count_beat() == 3 or count_beat() >= 2):
        print("   SNARE")
        drum.strike()



def tick():
    global ticks, prev_4, prev_8, prev_16
    ticks = ticks + 1
    if prev_4 != count_beat(): # nest these?
        hit_beat()
        prev_4 = count_beat()
    if prev_8 != count_8():
        hit_eighth()
        prev_8 = count_8()


def count_16():
    return (ticks // 8) % 4 # 0 beat, 1 "ee", 2 "and", 3 "ah"

def count_8():
    return (ticks // 16) % 2 # 0 is beat, 1 is "and"

def count_beat():
    return (ticks // 32) % 4


timer = timers.MeteredTimer(140, frequency, tick)
timer.start()
