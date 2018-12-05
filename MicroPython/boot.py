import time
import config
import leds
leds.all_off()

def connect(timeout=30):
    leds.all_on() # All on indicates scanning
    import network
    target = b'camp-manatee'
    sta_if = network.WLAN(network.STA_IF)

    # Returns list of SSIDs
    def get_available_networks():
        return [x[0] for x in sta_if.scan()]

    if not sta_if.isconnected():
        print('scanning networks...')
        sta_if.active(True)

        # Scan nearby Wifi Access Points 15 times, looking for the target
        for i in range(timeout//2):
            ssids = get_available_networks()
            print(ssids)
            # Once camp-manatee is found, try to connnect for 30 seconds
            # Blinking indicates attempting to connect
            if target in ssids:
                print("Found CAMP, connecting", end='')
                sta_if.connect('camp-manatee','iotwifipass')
                for i in range(timeout):
                    # Visual progress indicators
                    print('.',end='')
                    leds.blink_all(2) # Blink on 1 sec, blink off 1 sec
                    if sta_if.isconnected():
                        leds.show_success()
                        print("Woo! Connected to CAMP Manatee")
                        print('network config:', sta_if.ifconfig())
                        break
                print('')
                break
            print("Network not found. Retrying...")
            time.sleep(1)

        else:
            print("failed to connect, try again")
            leds.show_failure()

# Call to supress verbose wifi output
def no_debug():
    import esp
    esp.osdebug(None)

no_debug()
connect()

# Default sample. if this message prints then there is an error in
# another module or the config is invalid
def sample():
    print("No instrument type configured!")

# replace sample function with that of the proper instrument module
if config.instrument_type == 'guitar':
    import guitar
    sample = guitar.sample
if config.instrument_type == "drumpad":
    import drumpad
    sample = drumpad.sample

# For dev in the REPL, manually sample and inspect sensor readings
def do_n_samples(n):
    for i in range(n):
        sample(True)
        time.sleep_ms(config.sample_frequency)

# If config does not specify dev mode, begin sample loop
if not config.dev:
    while True:
        sample()
        time.sleep_ms(config.sample_frequency)
