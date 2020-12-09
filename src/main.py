from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, flash, url_for
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from flask_mqtt import Mqtt

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = ''
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1  # refresh time in seconds
app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SECRET_KEY'] = ''
mqtt = Mqtt(app)
socketio = SocketIO(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    changes = db.relationship('Updates', backref='author', lazy=True)


class Updates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Updates('{self.title}', '{self.content}','{self.date_updated}')"


@app.route("/")
def home():
    updates = db.session.query(User, Updates).order_by(Updates.date_updated.desc()).join(User).all()
    return render_template("index.html", updates=updates)


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('light/status')


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print("last status update: " + str(data))
    socketio.emit('status', data=data, broadcast=True)
    print("update sent successfully")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return flask.redirect(next or flask.url_for('login'))


@socketio.on('color')
def handleColor(msg):
    print('Color recieved: ' + msg)
    print('Sending via MQTT...')
    mqtt.publish('light/color', msg)
    change = Updates(title='Color change', content='Color changed to (' + msg +')', user_id=1)
    db.session.add(change)
    db.session.commit()
    new_line = db.session.query(User, Updates).order_by(Updates.date_updated.desc()).join(User).first()
    data = to_json(new_line)
    print(data)
    socketio.emit('db_update', data, broadcast=True)


@socketio.on('effect')
def handleColor(msg):
    print('Effect recieved: ' + msg)
    print('Sending via MQTT...')
    mqtt.publish('light/effects', msg)
    change = Updates(title='Effect change', content='Effect changed to ' + msg +'', user_id=1)
    db.session.add(change)
    db.session.commit()
    new_line = db.session.query(User, Updates).order_by(Updates.date_updated.desc()).join(User).first()
    data = to_json(new_line)
    print(data)
    socketio.emit('db_update', data, broadcast=True)


@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response


def to_json(data):
    """
    This function creates a dictionary and assigns
    the keys of the dictionary with the objects of
    the class and returns it in a json format. 
    """
    print(data.User.username)
    final = {
        'usuario': data.User.username,
        'cambio': data.Updates.title,
        'desc': data.Updates.content,
        'fecha': data.Updates.date_updated.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    }
    return final

if __name__ == "__main__":
    socketio.run(app, debug=True)


