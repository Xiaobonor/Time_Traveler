# app/utils/callback.py
from app import socketio


def status_callback(message, role="system", user_id=None):
    if message is not None:
        socketio.emit('status_update', {'message': message, 'role': role}, room=user_id)
