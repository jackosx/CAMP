from flask import Flask, request
from flask_cors import CORS
import paho.mqtt.publish as publish
from pythonosc import udp_client
from pythonosc import osc_message_builder
import socket


app = Flask(__name__)
CORS(app)
ip = socket.gethostbyname("dan.local")
client = udp_client.SimpleUDPClient(ip, 5005)

@app.route('/', methods=['POST'])
def parse_request():
    data = request.get_json()
    #publish.single(data['topic'], data['payload'], hostname="manatee.local")
    client.send_message(data['topic'], data['payload'])
    print(data['topic'])
    print(data['payload'])
    return 'sup'


if __name__ == '__main__':
    app.run(debug=True)
