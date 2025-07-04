from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='.')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

ladle_data = []  # Store history temporarily

@app.route('/')
def index():
    return render_template('ladle_monitoring_ui.html')  # Your HTML file

@socketio.on('new_entry')
def handle_new_entry(data):
    ladle_data.append(data)
    emit('update_dashboard', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
