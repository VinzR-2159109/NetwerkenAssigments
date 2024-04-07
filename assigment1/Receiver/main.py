from flask import Flask, jsonify, request, Response
import requests
import paho.mqtt.client as paho
import uuid
import time
import threading

app = Flask(__name__)

opened_items = []

# MQTT client setup
client = paho.Client(client_id=str(uuid.uuid4()), userdata=None, protocol=paho.MQTTv5, callback_api_version=paho.CallbackAPIVersion.VERSION2)

def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
    if rc == 0:
        print("MQTT Connected successfully")
    else:
        print("MQTT Connection failed with code %d" % rc)

client.on_connect = on_connect
client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
client.username_pw_set("VinzRoosen", "cnVlz@QoG2vTTvyO")

client.connect("7fff47e5b4c74408957f70f5064d717b.s1.eu.hivemq.cloud", 8883)

def publish_file_received(file_id):
    client.publish("fileServer", payload="file received: " + file_id, qos=1)

@app.route('/get_file', methods=['GET'])
def get_file():
    file_id = request.args.get('value')

    if not file_id:
        return jsonify({'error': 'File ID is missing'}), 400

    url = f'https://file.io/{file_id}'
    response = requests.get(url)

    if response.ok:
        content = response.content
        content_type = response.headers['Content-Type']

        headers = {
            'Content-Disposition': f'attachment; filename=file_{file_id}',
            'Content-Type': content_type
        }

        opened_items.append(file_id)
        threading.Thread(target=publish_file_received, args=(file_id,)).start()

        return Response(content, headers=headers)
    else:
        return jsonify({'error': 'Failed to fetch file'}), response.status_code

@app.route('/get_ack', methods=['GET'])
def get_ack():
    return jsonify(opened_items)

client.loop_start()

if __name__ == '__main__':
    app.run(debug=True)
