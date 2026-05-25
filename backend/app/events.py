from flask import request
from flask_socketio import emit
from .extensions import socketio

_user_sid_map: dict[int, str] = {}


@socketio.on("connect")
def on_connect():
    print("SocketIO connected:", request.sid)


@socketio.on("join_user")
def on_join_user(data):
    user_id = data.get("user_id")
    if user_id:
        _user_sid_map[int(user_id)] = request.sid
        socketio.server.enter_room(request.sid, f"user_{user_id}")


@socketio.on("disconnect")
def on_disconnect():
    for uid, sid in list(_user_sid_map.items()):
        if sid == request.sid:
            del _user_sid_map[uid]
    print("SocketIO disconnected:", request.sid)
