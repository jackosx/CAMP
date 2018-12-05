import time

def connect(timeout=30):
    import network
    target = b'camp-manatee'
    sta_if = network.WLAN(network.STA_IF)
    def get_available_networks():
        return [x[0] for x in sta_if.scan()]
    if not sta_if.isconnected():
        print('scanning networks...')
        sta_if.active(True)
        for i in range(timeout):
            ssids = get_available_networks()
            if target in ssids:
                print("Found CAMP, connecting", end='')
                sta_if.connect('camp-manatee','iotwifipass')
                for i in range(timeout):
                    print('.',end='')
                    time.sleep(1)
                    if sta_if.isconnected():
                        print("Woo! Connected to CAMP Manatee")
                        print('network config:', sta_if.ifconfig())
                        break
                print('')
                break

            print(ssids)
            print("Network not found. Retrying...")
            time.sleep(1)

        else:
            print("failed to connect, try again")

def no_debug():
    import esp
    # you can run this from the REPL as well
    esp.osdebug(None)

# no_debug()
connect()

def sample():
    print("No instrument type configured!")

# def samp_guitar(calls, freq, v=False):
#     for i in range(calls):
#         guitar.sample(v)
#         time.sleep_ms(freq)

import config
if config.instrument_type == 'guitar':
    import guitar
    sample = guitar.sample
if config.instrument_type == "drumpad":
    import drumpad
    sample = drumpad.sample

def do_n_samples(n):
    for i in range(n):
        sample(config.dev)
        time.sleep_ms(config.sample_frequency)

if not config.dev:
    while True:
        sample()
        time.sleep_ms(config.sample_frequency)
