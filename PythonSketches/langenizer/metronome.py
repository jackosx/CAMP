import queue
import timers

ticks = 0
frequency = 32 # 32 ticks per beat
meter = 4

prev_4 = -1
prev_8 = -1
prev_16 = -1

q4  = queue.Queue()
q8  = queue.Queue()
q16 = queue.Queue()

items = ()

def on_next_beat(f, *args, **kwargs):
    q4.put((f, args, kwargs))

def hit_beat():
    global prev_4
    prev_4 = count_beat()
    while not q4.empty():
        global items
        items = q4.get_nowait()
        f, args, kwargs = items[0], items[1], items[2]
        f(*args, **kwargs)

def hit_eighth():
    global prev_8
    prev_8 = count_8()


def tick():
    global ticks
    ticks = ticks + 1
    if prev_4 != count_beat(): # nest these?
        hit_beat()
    if prev_8 != count_8():
            hit_eighth()

def count_16():
    return (ticks // 8) % 8

def count_8():
    return (ticks // 16) % 4

def count_beat():
    return (ticks // 32) % 4

ticker = timers.MeteredTimer(120, frequency, tick)
