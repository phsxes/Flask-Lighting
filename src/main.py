from flask import Flask, render_template, request, jsonify
from flask_mqtt import Mqtt

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'ioticos.org'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'VRKGqSXh5nVPALh'
app.config['MQTT_PASSWORD'] = 'NGz4VIMwF0vaxOc'
app.config['MQTT_REFRESH_TIME'] = 0.5  # refresh time in seconds
mqtt = Mqtt(app)

@app.route("/")
def home():
    return render_template("index.html")

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('9J3TptLmLQKGGks/input')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

    print(data['payload'])
if __name__ == "__main__":
    app.run(debug=False)


