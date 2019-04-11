
from pythonosc import osc_message_builder
from pythonosc import udp_client
import time

# # Set up MQTT (should be OSC?)
# def on_connect_mqtt(client, userdata, flags, rc):
#     print("Connected to MQTT with result code "+str(rc))
#     # Subscribing in on_connect() means that if we lose the connection and
#     # reconnect then subscriptions will be renewed.
#
# # The callback for when a PUBLISH message is received from the server.
# def on_message_mqtt(client, userdata, msg):
#     print("Unhandled message:" + msg.topic+" "+str(msg.payload))

client = udp_client.SimpleUDPClient("jack.local", 5005)

class Guitar(object):
    """Mock ESP32 Guitar."""
    def __init__(self, id=0):
        super(Guitar, self).__init__()
        self.fret = id
        self.id = id
    # Actual strum message from ESP32 upython:
    # mannet.send_message('/i/g/{}/d/s'.format(guitar_id), str(v))
    def strum(self,vel=90):
        client.send_message('/i/g/{}/d/s'.format(self.id), str(min(vel,127)))
    def change_fret(self,fret=0):
        self.fret = fret
        client.send_message('/i/g/{}/d/f'.format(self.id), str(self.fret))
    def strum_fret(self, fret=0,velocity=90):
        self.change_fret(fret)
        time.sleep(.001)
        self.strum(velocity)


class Drumstick(object):
    """Mock ESP32 Drumstick."""
    def __init__(self, id=0):
        super(Drumstick, self).__init__()
        self.id = id
    # Actual strum message from ESP32 upython:
    # mannet.send_message('/i/d/{}/d/s/{}'.format(drumstick_id, 0), str(min(velocity, 127)))
    def strike(self,vel=90):
        client.send_message('/i/d/{}/d/s/{}'.format(self.id, 0), str(min(vel, 127)))
