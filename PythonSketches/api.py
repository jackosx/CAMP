from flask import Flask, request
from flask_cors import CORS
import paho.mqtt.publish as publish

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['POST'])
def parse_request():
    data = request.get_json()
    publish.single(data['topic'], data['payload'], hostname="manatee.local")
    print(data['topic'])
    print(data['payload'])
    return 'sup'


if __name__ == '__main__':
    app.run(debug=True)
