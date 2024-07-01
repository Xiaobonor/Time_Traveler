# app/socket_handlers/connect_disconnect.py
from flask import session
from flask_socketio import emit, join_room
from app import socketio

@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_info')['google_id']
    if user_id:
        join_room(user_id)
        emit('status_update', {'message': '🌐 伺服器連線成功'}, room=user_id)
