import network
import leds
from umqtt.simple import MQTTClient
from uosc.client import Bundle, Client, create_message
import config

sta_if = network.WLAN(network.STA_IF)
target = b'camp-manatee'
mqtt   = None
osc    = None
mdns   = network.mDNS()

# Returns list of SSIDs
def get_available_networks():
    return [x[0] for x in sta_if.scan()]

def is_connected():
    return sta_if.isconnected()

# Default behavior is connect to OSC, specify mqtt client name for MQTT
def connect_client(host="jack", port=5005, mqtt_client_name=None):
    global mqtt, osc
    ip = mdns.queryHost(host)
    if mqtt_client_name is not None:
        mqtt = MQTTClient(mqtt_client_name, ip)
        mqtt.connect()
    else: # use OSC
        osc = Client(ip, port)

def send_message(channel="/", msg=""):
    if mqtt is not None:
        mqtt.publish(channel, msg)
    if osc is not None:
        osc.send(channel, msg)

def connect_wifi(target=b'camp-manatee', timeout=30):
    leds.all_on() # All on indicates scanning

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
                sta_if.connect(target,'ronlasser')
                for i in range(timeout):
                    # Visual progress indicators
                    print('.',end='')
                    leds.blink_all(2) # Blink on 1 sec, blink off 1 sec
                    if sta_if.isconnected():
                        leds.show_success()
                        print("Woo! Connected to CAMP Manatee")
                        print('network config:', sta_if.ifconfig())
                        mdns.start("ESP32", "ESP32 MicroPython Instrument")
                        break
                print('')
                break
            print("Network not found. Retrying...")
            time.sleep(1)

        else:
            print("failed to connect, try again")
            leds.show_failure()
