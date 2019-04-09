"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
        help="The ip of the OSC server")
    parser.add_argument("--inst", default="guitar",
        help="The instrument to simulate")
    parser.add_argument("--port", type=int, default=5005,
        help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)

    if args.inst == "guitar":
        client.send_message("/i/g/0/d/s", 100)
    elif args.inst == "drums" or args.inst == "drum":
        client.send_message("/i/d/0/d/s/0", 100)
