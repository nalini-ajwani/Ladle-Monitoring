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
    # Prevent duplicate "Enter LF" or "Enter Caster"
    if len(ladle_data) > 0:
        last_process = ladle_data[-1].get("process")
        if (data["process"] in ["Enter LF", "Enter Caster"]) and (last_process == data["process"]):
            emit("error_message", {"error": "Duplicate LF/Caster not allowed"}, room=request.sid)
            return

    ladle_data.append(data)
    save_data()
    emit('update_dashboard', data, broadcast=True)

if __name__ == '__main__':
    load_data()
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

