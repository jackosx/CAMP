from pynput import keyboard
from langenizer import midi

guitar = midi.Guitar()
keys_pressed = set()
valid_keys = {'a', 'b', 'c', 'd', 'e', 'f', 'g'}

def on_press(key):
    try:
        if key not in keys_pressed:
            keys_pressed.add(key)
            if key == keyboard.Key.space:
                guitar.strum()
                return
            k = key.char
            if k.isalpha() and k in valid_keys:
                guitar.play_note(k)
            if k.isdigit() and int(k) < 5:
                guitar.set_fret(int(k))
            if k == 's':
                guitar.strum()
            if k == 'p':
                guitar.stop_all()
        # print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))
    except ValueError:
        print('error playing note')

def on_release(key):
    # print('{0} released'.format(key))
    keys_pressed.remove(key)
    if key == keyboard.Key.esc:
        # Stop listener
        return False
    if key == keyboard.Key.space:
        return
    try:
        k = key.char
        if k.isalpha() and k in valid_keys:
            guitar.stop_note(k)
        elif k.isdigit():
            guitar.set_fret(0)
    except AttributeError:
        print('special key {0} pressed'.format(key))


# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
