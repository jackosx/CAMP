import time
import config
import mannet

# Connect to camp-manatee
mannet.connect_wifi()

# Default sample. if this message prints then there is an error in
# another module or the config is invalid
def sample():
    print("No instrument type configured!")
def calibrate():
    print("No instrument type configured!")

# replace sample function with that of the proper instrument module
if config.instrument_type == 'guitar':
    import guitar
    sample    = guitar.sample
    calibrate = guitar.calibrate
if config.instrument_type == "drumpad":
    import drumpad
    sample    = drumpad.sample
    calibrate = drumpad.calibrate
if config.instrument_type == 'drumstick':
    import drumstick
    sample    = drumstick.sample
    # calibrate = drumstick.calibrate

calibrate()

# For dev in the REPL, manually sample and inspect sensor readings
def do_n_samples(n):
    for i in range(n):
        sample(True)
        time.sleep_ms(config.sample_frequency)


while True:
    sample(config.dev)
    time.sleep_ms(config.sample_frequency)
