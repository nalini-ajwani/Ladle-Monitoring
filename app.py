from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

DATA_FILE = "ladle_data.json"
ladle_data = []

def load_data():
    global ladle_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            ladle_data = json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(ladle_data, f)

@app.route('/')
def index():
    return render_template('ladle_monitoring_ui.html')

@app.route('/get_data')
def get_data():
    return jsonify(ladle_data)

@app.route('/clear_data', methods=['POST'])
def clear_data():
    global ladle_data
    ladle_data = []
    save_data()
    return jsonify({"status": "cleared"})

@socketio.on('new_entry')
def handle_new_entry(data):
    global ladle_data

    # Remove any existing entry for this ladle
    ladle_data = [d for d in ladle_data if d["ladleNo"] != data["ladleNo"]]

    # Add new entry
    ladle_data.append(data)
    save_data()
    emit('update_dashboard', data, broadcast=True)

@socketio.on('delete_entry')
def handle_delete_entry(data):
    global ladle_data
    ladle_data = [d for d in ladle_data if d["ladleNo"] != data["ladleNo"]]
    save_data()
    emit('update_dashboard', {}, broadcast=True)

if __name__ == '__main__':
    load_data()
    socketio.run(app, host='0.0.0.0', port=5000)
