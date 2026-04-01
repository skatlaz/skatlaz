from flask_socketio import SocketIO, emit, join_room

socketio = SocketIO(cors_allowed_origins="*")

def init_socket(app):
    socketio.init_app(app)

@socketio.on("join")
def join(data):
    join_room(data["room"])

@socketio.on("send")
def send(data):
    emit("msg", data, room=data["room"])

def send_alert(socketio, msg):
    socketio.emit("alert", {"msg": msg})
