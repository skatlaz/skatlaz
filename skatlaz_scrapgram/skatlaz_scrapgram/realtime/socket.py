from flask_socketio import emit, join_room

def register_events(socketio):

    @socketio.on("join")
    def join(data):
        join_room(data["room"])

    @socketio.on("message")
    def message(data):
        emit("message", data, room=data["room"])
