from pynput import keyboard
from langenizer import midi

guitar = midi.Instrument()
keys_pressed = set()

def on_press(key):
    try:
        if key.char not in keys_pressed:
            keys_pressed.add(key.char)
            guitar.play_note(key.char)
        # print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))
    except ValueError:
        print('error playing note')

def on_release(key):
    # print('{0} released'.format(key))
    try:
        keys_pressed.remove(key.char)
        if key.isalpha():
            guitar.stop_note(key.char)

    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
